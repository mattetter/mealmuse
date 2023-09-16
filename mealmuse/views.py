# views.py is the file that contains all the routes for our application.
from . import login_manager, db
import json
import datetime
from datetime import date
from flask import Blueprint
from flask import flash, redirect, render_template, request, session, url_for, current_app, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from .forms import RegistrationForm, LoginForm, BugReportForm  # import the forms
from .models import User, Pantry, Item, ShoppingList, MealPlan, Recipe, PantryItem, ShoppingListItem, Meal, Day, Diet, Allergy, UserProfile, BugReport  # import the models
from .utils import get_meal_plan, get_meal_plan_details, get_recipe_details_by_ids, extract_recipe_ids, get_user_profile, create_blank_meal_plan, check_for_incomplete_meal_plan, save_day, add_item_to_list, add_missing_or_all_items_to_shopping_list, remove_recipe_items_from_pantry, update_item_quantity # import the utility functions
from mealmuse.tasks import swap_out_recipe, generate_new_recipe
from werkzeug.security import generate_password_hash, check_password_hash
from .exceptions import InvalidOutputFormat


# Create a Blueprint instance
views = Blueprint('views', __name__)


@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Query the database for the user
        user = User.query.filter_by(username=username).first()

        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, password):
            # Log the user in
            login_user(user)

            # Redirect to the dashboard or wherever you want
            return redirect(url_for('views.index'))
        else:
            # If the login doesn't match, show an error message
            flash('Invalid username or password.')
    return render_template('login.html')

@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.login'))


@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:

            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirmation')

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists. Please choose another one.', 'danger')
                return render_template('register.html')

            if not username or not password or not confirm_password:
                flash('All fields are required.', 'danger')
            elif password != confirm_password:
                flash('Passwords do not match.', 'danger')
            else:
                hashed_password = generate_password_hash(password, method='sha256')
                new_user = User(username=username, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()

                # Create a pantry for the user
                pantry = Pantry(user_id=new_user.id)
                db.session.add(pantry)

                # Create a shopping list for the user
                shopping_list = ShoppingList(user_id=new_user.id)
                db.session.add(shopping_list)

                # Create a user profile for the user
                user_profile = UserProfile(user_id=new_user.id)
                db.session.add(user_profile)
                db.session.commit()

                flash('You have been registered successfully.', 'success')
                return redirect(url_for('views.login'))
        except Exception as e:
            flash("An error occurred while processing your request.", 'danger')
            db.session.rollback()
            print(f"Error occurred: {e}")
            db.session.remove()
            raise
            return render_template('register.html')

    return render_template('register.html')


#automatically create tables and log in test user
@views.before_request
def before_request():
        # redirect to login page
    # allowed_routes = ['login', 'register', 'report_bug']
    # if request.endpoint not in [f'views.{route}' for route in allowed_routes]:
    #     if not current_user.is_authenticated:
    #         return redirect(url_for('views.login'))
    
    # # USE THIS ONLY FOR TESTING PURPOSES
    if not current_user.is_authenticated:
        
        # check if the test user exists
        user = User.query.filter_by(username="testuser").first()
        if not user:
            # Create a test user
            user = User(id=1, username="testuser", email="testuser@email.com", password=generate_password_hash("testpassword"))
            db.session.add(user)
            db.session.commit()

            # Create a pantry for the user
            pantry = Pantry(user_id=user.id)
            db.session.add(pantry)

            # Create a shopping list for the user
            shopping_list = ShoppingList(user_id=user.id)
            db.session.add(shopping_list)

            # Create a user profile for the user
            user_profile = UserProfile(user_id=user.id)
            db.session.add(user_profile)
            db.session.commit()
            

        # log the user in
        login_user(user)


@views.route('/pantry')
@login_required
def pantry():
    # Assume we have a current_user object that represents the logged-in user
    user = User.query.get(current_user.id)

    if not user.pantry:
        pantry = Pantry(user=user)
        db.session.add(pantry)
        db.session.commit()

    # Fetch pantry and shopping list items for the current user from the database
    pantry_items = user.pantry.pantry_items if user.pantry else []

    return render_template('pantry.html', pantry_items=pantry_items)



@views.route('/shopping_list')
@login_required
def shopping_list():
    # Assume we have a current_user object that represents the logged-in user
    user = User.query.get(current_user.id)

    if not user.shopping_list:
        shopping_list = ShoppingList(user=user)
        db.session.add(shopping_list)

    db.session.commit()

    shopping_list_items = user.shopping_list.shopping_list_items if user.shopping_list else []

    return render_template('shopping_list.html', shopping_list_items=shopping_list_items)


@views.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity') or 1
        unit = request.form.get('unit')  # Get unit if available
        list_type = request.form.get('list_type')
        add_item_to_list(current_user, name, quantity, list_type, unit)

    referrer = request.referrer
    return redirect(referrer)


# Edit an existing item in the pantry or shopping list
@views.route('/remove_item/<string:list_type>/<int:item_id>')
def remove_item(list_type, item_id):
    referrer = request.referrer
    if list_type == "pantry":
        item = PantryItem.query.get(item_id)
    elif list_type == "shopping_list":
        item = ShoppingListItem.query.get(item_id)
    else:
        flash("Invalid list type!")
        return redirect(referrer)

    if item:
        db.session.delete(item)
        db.session.commit()
    else:
        flash("Item not found!")
    
    return redirect(referrer)


# Edit an existing item in the pantry or shopping list
@views.route('/mark_as_purchased/<int:item_id>')
def mark_as_purchased(item_id):
    referrer = request.referrer
    item = ShoppingListItem.query.get(item_id)
    name = item.item.name
    quantity = item.quantity
    unit = item.unit
    add_item_to_list(current_user, name, quantity, "pantry", unit)

    db.session.delete(item)
    db.session.commit()

    return redirect(referrer)

# add the ingredients for a recipe to the shopping list
@views.route('/add_group_to_shopping_list', methods=['POST'])
def add_group_to_shopping_list():
    recipe_id = request.form.get('recipe_id')
    action = request.form.get('action', 'add_missing')  # Default to 'add_missing' if not specified
    recipe = Recipe.query.get(recipe_id)  # Replace with your logic to get the recipe

    add_missing_or_all_items_to_shopping_list(current_user, recipe, action)

    referrer = request.referrer
    return redirect(referrer)


@views.route('/remove_ingredients_from_pantry/<int:recipe_id>', methods=['POST'])
def remove_ingredients_from_pantry(recipe_id):
    # Fetch recipe details using recipe_id from the database.
    recipe = db.session.query(Recipe).filter_by(id=recipe_id).first()
    if not recipe:
        flash('Recipe not found!', 'error')
        return redirect(url_for('views.all_recipes'))

    # Mark the recipe as completed 
    # ...

    # Remove ingredients from the user's pantry
    remove_recipe_items_from_pantry(current_user, recipe)

    flash('Recipe marked as completed and ingredients removed from pantry.', 'success')
    referrer = request.referrer
    return redirect(referrer)


# the homescreen
@views.route("/", methods=("GET", "POST"))
@login_required
def index():
    if 'redirect_count' in session:
        del session['redirect_count']
    if request.method == "POST":

        return render_template("index.html", error_message="An error occurred while generating your meal plan. Please try again.")

    else:  # GET request
        # get the most recent meal plan for the user
        serialized_meal_plan = get_meal_plan_details(current_user)
        # check if meal plan contains recipes for the current day 
        today_recipes = False
        if serialized_meal_plan:
            for day in serialized_meal_plan['days']:
                if day['date'] == date.today():
                    for meal in day['meals']:
                        if meal['recipes']:
                            today_recipes = True
                            break
                    if today_recipes:
                        break



        return render_template('index.html', meal_plan=serialized_meal_plan, today_recipes=today_recipes, datetime=datetime)


# Meal Plan: main page for creating and modifying meal plans
@views.route("/meal_plan", methods=["GET", "POST"])
@login_required
def meal_plan(meal_plan=None):
    # Error handling for incomplete meal plans
    # check if meal_plan_id is in the session, if so pop it, check if it is not valid if so delete if from the database and the session
    check_for_incomplete_meal_plan(session)

    #Error handling for too many redirects, crazy infrequent bug :( 
    if 'redirect_count' in session:
        del session['redirect_count']
    
    if meal_plan:
        meal_plan_to_display = meal_plan
    else:
        # if there are any valid meal plans in the database, fetch the most recent one
        meal_plan_to_display = get_meal_plan_details(current_user)

    if request.method == "POST":
        # You can handle the logic when the form data is posted, such as saving the data into your database

        return redirect(url_for('views.meal_plan'))
    else:

        # Pass attributes to the template
        return render_template('meal_plan.html', datetime=datetime, meal_plan=meal_plan_to_display)


# Meal Plan: pick which days to plan for
@views.route('/day_selections', methods=['GET', 'POST'])
def day_selections():
    formatted_selected_days = []
    user = User.query.get(current_user.id)
    if request.method == 'POST':
        # Get the checked days from the form data
        selected_days = request.form.getlist('day')
        #Get the requested cuisine from the form data
        preferred_cuisine = request.form.get('preferred_cuisine')
        # Save the new meal plan using utility function
        meal_plan_id = create_blank_meal_plan(current_user.id, preferred_cuisine).id

        # Add the meal plan to the session for the next route.
        session['meal_plan_id'] = meal_plan_id

        for day_str in selected_days:
            # Convert string back to datetime object for displaying
            day_dt = datetime.datetime.fromisoformat(day_str).date()
            formatted_day = day_dt.strftime('%A, %B %d')
            formatted_selected_days.append(formatted_day)

        # Save the selected days in session
        session['selected_days'] = selected_days
        session['current_day_index'] = 0

        return redirect(url_for('views.select_items'))

    return render_template('day_selections.html', datetime=datetime)

# Select a budget for your meal plan
@views.route('/budget_selection', methods=['GET', 'POST'])
def budget_selection():
    if request.method == 'POST':
        # Get the selected budget from the form data
        selected_budget = request.form.get('budget')

        # get the mealplan from the session
        meal_plan_id = session['meal_plan_id']
        meal_plan = MealPlan.query.get(meal_plan_id)

        # Save the selected budget in the database
        meal_plan.budget = selected_budget
        db.session.commit()

        return redirect(url_for('views.pantry_use'))

    return render_template('budget_selection.html', datetime=datetime)



# Meal Plan; Choose how much to rely on pantry items
@views.route('/pantry_use', methods=['GET', 'POST'])
def pantry_use():
    if request.method == 'POST':
        # Get the selected family size from the form data
        pantry_use = request.form.get('pantry use')

        # get the mealplan from the session
        meal_plan_id = session['meal_plan_id']
        meal_plan = MealPlan.query.get(meal_plan_id)

        # Save the selected budget in the database
        meal_plan.pantry_use = pantry_use
        db.session.commit()

        return redirect(url_for('views.select_items'))

    return render_template('pantry_use.html', datetime=datetime)

# Meal Plan; Choose how much to rely on leftovers
@views.route('/leftovers', methods=['GET', 'POST'])
def leftovers():
    if request.method == 'POST':
        # Get the selected family size from the form data
        leftovers = request.form.get('leftovers')

        # Save the selected number in the database
        # get the mealplan from the session
        meal_plan_id = session['meal_plan_id']
        meal_plan = MealPlan.query.get(meal_plan_id)

        # Save the selected budget in the database
        meal_plan.leftovers = leftovers
        db.session.commit()

        return redirect(url_for('views.select_items'))

    return render_template('leftovers.html', datetime=datetime)


# Meal plan; takes user selections for each day, saves the day to the meal plan, and increments the day index. 
# If all days have been processed, redirects to loading screen
@views.route('/select_items', methods=['GET', 'POST'])
def select_items():
    if 'selected_days' not in session or 'current_day_index' not in session:
        flash("No day selected!", "error")
        return redirect(url_for('views.meal_plan'))
    
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    default_family_size = user_profile.family_size if user_profile else 1
    
    if request.method == 'POST':
        # Get the selected items from the form data
        meals_data = {}
        checked_meals = request.form.getlist('meals')  # This will give a list of checked meals
        for meal in checked_meals:  # Loop over checked meals only
            meals_data[meal] = {
                "time": request.form.get(f"{meal}-time"),
                "people": request.form.get(f"{meal}-people"),
                "cuisine": request.form.get(f"{meal}-cuisine"),
                "type": request.form.get(f"{meal}-type")
            }
        # Handle the selected items and save to the meal plan
        # Save to your DB, using the meal_plan_id from the session.
        meal_plan_id = session.get('meal_plan_id')
        if not meal_plan_id:
            flash("Invalid meal plan!", "error")
            return redirect(url_for('views.index'))

        # Fetch or create the day
        if 'current_day_index' in session and 'selected_days' in session:
            current_day_str = session['selected_days'][session['current_day_index']]
            current_day_datetime = datetime.datetime.fromisoformat(current_day_str)
        else:
            flash("Day index or selected days not found in session.", "error")
            return redirect(url_for('views.some_route'))

        # Save the day to the current meal plan
        if not meals_data:
            # If no meals are selected for the day, don't save it
            flash("No selections made for the day!", "warning")
            # redirect to the same page
            return redirect(url_for('views.select_items'))
        else:
            # Save the day to the current meal plan
            save_day(meal_plan_id, current_day_datetime, meals_data)


        # Increment the day index for the next day
        session['current_day_index'] += 1

        # Check if we have processed all the days
        if session['current_day_index'] >= len(session['selected_days']):

            # mark the meal plan as a valid meal plan so it doesn't get deleted
            meal_plan = MealPlan.query.get(meal_plan_id)
            user_id = current_user.id
            meal_plan.status = "generating"
            db.session.commit()
            db.session.close()
            # generate the meal plan
            get_meal_plan(meal_plan_id, user_id)
 
            # Cleanup session
            del session['selected_days']
            del session['current_day_index']
            del session['meal_plan_id']

            return redirect(url_for('views.meal_plan'))
    
    current_day = session['selected_days'][session['current_day_index']]
    current_day_datetime = datetime.datetime.strptime(current_day, "%Y-%m-%dT%H:%M:%S.%f")

    #Error handling for too many redirects
    if 'redirect_count' not in session:
        session['redirect_count'] = 0

    if session['redirect_count'] > 8:  # or any threshold you find suitable
        flash("Too many redirects. Breaking the loop.", "error")
        session.pop('redirect_count', None)  # Reset the count
        return redirect(url_for('views.index'))

    session['redirect_count'] += 1

    # Format the date to display
    formatted_day = current_day_datetime.strftime("%A, %B %d")
    return render_template('select_items.html', current_day=formatted_day, datetime=datetime, default_family_size=default_family_size)


# Meal Plan: loading screen
@views.route('/meal_plan_loading', methods=['GET'])
def meal_plan_loading():

    return  render_template('meal_plan_loading.html', datetime=datetime)


# doing the actual work of generating the meal plan here in order to render a loading screen
@views.route('/generate_meal_plan', methods=['POST'])
def generate_meal_plan():
    #get the user from session
    user = User.query.get(current_user.id)
    # get the meal_plan from the session
    meal_plan_id = session['meal_plan_id']
    meal_plan = MealPlan.query.get(meal_plan_id)

    #clean up session
    del session['meal_plan_id']

    # generate the meal_plan with the current app object
    meal_plan = get_meal_plan(meal_plan.id, user.id)

    return jsonify(status="success", message="Meal plan generated!")


# Recipe generation; takes parameters of a given recipe and replaces it with a new one
@views.route('/change_recipe', methods=['POST'])
def change_recipe():
    # get the recipe id from the form data
    recipe_id = request.form.get('recipe_id')
    user_id = current_user.id
    swap_out_recipe.delay(recipe_id, user_id)
    print("recipe swap task sent to celery")
    # return the user to the meal plan page, the new recipe will  be there once it is done processing
    return redirect(url_for('views.meal_plan'))


# Recipe generation; make selections for a single new recipe
@views.route('/recipe_selections' , methods=['GET', 'POST'])
def recipe_selections():
    if request.method == 'POST':
        return redirect(url_for('/'))
    else:
        # handle GET request
        return render_template('recipe_selections.html', datetime=datetime)


# Recipe generation; creates a new recipe with only the ingredients listed in the pantry
@views.route('/generate_recipe', methods=['GET', 'POST'])
def generate_recipe():
    if request.method == 'POST':
        # Get the selected family size from the form data
        serves = request.form.get('serves') or None
        time = request.form.get('time') or None
        cuisine = request.form.get('cuisine') or None
        
        new_recipe = Recipe(
            name="please generate",
            cuisine=cuisine,
            time=time,
            serves=serves,
        )
        db.session.add(new_recipe)
        db.session.commit()

        user_id = current_user.id

        recipe_id = new_recipe.id
        db.session.close()

        recipe = generate_new_recipe.delay(user_id, recipe_id)

        return redirect(url_for('views.recipe_page', recipe_id=new_recipe.id))


# Displays a given recipe in the meal plan page
@views.route('/recipe/<int:recipe_id>', methods=['GET'])
def recipe_page(recipe_id):
    # Fetch recipe details using recipe_id from the database.
    recipe = db.session.query(Recipe).filter_by(id=recipe_id).first()
    if not recipe:
        flash('Recipe not found!', 'error')
        return redirect(url_for('views.meal_plan'))

    # Render the recipe details page.
    return render_template('recipe.html', recipe=recipe)


# Displays all recipes for a given user
@views.route('/all_recipes', methods=['GET'])
def all_recipes():
    # make a list of all recipes for the current user from the database using the user.recipes relationship
    recipes = []
    for recipe in current_user.recipes:
        recipes.append(recipe)


    # Render the all_recipes.html page and pass the recipes to it
    return render_template('all_recipes.html', recipes=recipes)


# Delete a recipe from the database
@views.route('/delete_recipe/<int:recipe_id>', methods=['GET'])
def delete_recipe(recipe_id):
    # Fetch recipe details using recipe_id from the database.
    recipe = db.session.query(Recipe).filter_by(id=recipe_id).first()
    if not recipe:
        flash('Recipe not found!', 'error')
        return redirect(url_for('views.all_recipes'))

    # Delete the recipe
    db.session.delete(recipe)
    db.session.commit()

    flash('Recipe deleted successfully.', 'success')

    referrer = request.referrer
    return redirect(referrer)


#Profile: main route
@views.route('/profile', methods=["GET"])
@login_required
def profile():
    user = User.query.get(current_user.id)
    
    # Check if the user has a profile, if not create one
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    # Extract lists of allergies and dietary restrictions for the user
    allergies = [allergy.name for allergy in user.allergies]
    dietary_restrictions = [diet.name for diet in user.diets]

    return render_template('profile.html', allergies=allergies, dietary_restrictions=dietary_restrictions, profile=profile)


# Profile: choose your proficiency level
@views.route('/proficiency', methods=['GET', 'POST'])
def proficiency():
    if request.method == 'POST':
        # get the selected proficiency level from the form data
        proficiency = request.form.get('proficiency')

        # save the selected proficiency in the database
        # Fetch the user's profile
        profile = UserProfile.query.filter_by(user_id=current_user.id).first()

        # Update the profile
        profile.proficiency = proficiency
        db.session.commit()


        flash("Proficiency updated successfully!", "success")
        return redirect(url_for('views.profile'))

    return redirect(url_for('views.profile'))

# Profile: Choose family size for meal plan
@views.route('/family_size', methods=['GET', 'POST'])
def family_size():
    if request.method == 'POST':
        # Get the selected family size from the form data
        family_size = request.form.get('family_size')

        # Save the selected number in the database
        # Fetch the user's profile
        profile = UserProfile.query.filter_by(user_id=current_user.id).first()

        # Update the profile
        profile.family_size = family_size
        db.session.commit()

        flash("Family size updated successfully!", "success")
        return redirect(url_for('views.profile'))

    return redirect(url_for('views.profile'))

    
@views.route('/add_dietary_restriction', methods=["POST"])
@login_required
def add_dietary_restriction():
    restriction_name = request.form.get("restriction")
    if not restriction_name:
        #flash error and return to last page
        flash('Please enter a dietary restriction.', 'danger')
        return redirect(url_for('views.profile'))
    restriction = Diet.query.filter_by(name=restriction_name).first()
    if not restriction:
        restriction = Diet(name=restriction_name)
        db.session.add(restriction)

    # Associate the restriction with the current user
    if restriction not in current_user.diets:
        current_user.diets.append(restriction)
    else:
        flash('Dietary restriction already added.', 'warning')
        return redirect(url_for('views.profile'))

    db.session.commit()
    flash('Dietary restriction added successfully.', 'success')
    return redirect(url_for('views.profile'))

@views.route('/add_allergy', methods=["POST"])
@login_required
def add_allergy():
    allergy_name = request.form.get("allergy")
    if not allergy_name:
        flash('Please enter an allergy.', 'danger')
        return redirect(url_for('views.profile'))

    allergy = Allergy.query.filter_by(name=allergy_name).first()
    if not allergy:
        allergy = Allergy(name=allergy_name)
        db.session.add(allergy)

    # Associate the allergy with the current user
    if allergy not in current_user.allergies:
        current_user.allergies.append(allergy)
    else:
        flash('Allergy already added.', 'warning')
        return redirect(url_for('views.profile'))

    db.session.commit()
    flash('Allergy added successfully.', 'success')
    return redirect(url_for('views.profile'))


@views.route('/remove_dietary_restriction/<restriction_name>')
@login_required
def remove_dietary_restriction(restriction_name):
    restriction = Diet.query.filter_by(name=restriction_name).first()
    if restriction and restriction in current_user.diets:
        current_user.diets.remove(restriction)
        db.session.commit()
        flash('Dietary restriction removed successfully.', 'success')
    else:
        flash('Dietary restriction not found.', 'danger')
    return redirect(url_for('views.profile'))

@views.route('/remove_allergy/<allergy_name>')
@login_required
def remove_allergy(allergy_name):
    allergy = Allergy.query.filter_by(name=allergy_name).first()
    if allergy and allergy in current_user.allergies:
        current_user.allergies.remove(allergy)
        db.session.commit()
        flash('Allergy removed successfully.', 'success')
    else:
        flash('Allergy not found.', 'danger')
    return redirect(url_for('views.profile'))


@views.route("/update_meal_plan_settings", methods=["POST"])
@login_required
def update_meal_plan_settings():
    try:
        family_size = int(request.form.get('FamilySize'))
        cuisine_requests = request.form.get('CuisineRequests')
        budget = int(request.form.get('Budget'))
        pantry_use = float(request.form.get('PantrySlider'))
        leftovers = float(request.form.get('LeftoversSlider'))
        proficiency = request.form.get('Proficiency')

        # Fetch the user's profile
        profile = UserProfile.query.filter_by(user_id=current_user.id).first()
        
        # Update the profile
        profile.family_size = family_size
        profile.cuisine_requests = cuisine_requests
        profile.budget = budget
        profile.pantry_use = pantry_use
        profile.leftovers = leftovers
        profile.proficiency = proficiency
        
        db.session.commit()

        flash("Meal Plan Settings updated successfully!", category="success")

    except Exception as e:
        flash(f"Error updating settings: {e}", category="error")

    return redirect(url_for('views.meal_plan'))


# Update both recipe and meal plan temperatures change randomness of api output
@views.route('/update_temperatures', methods=["POST"])
@login_required
def update_temperatures():
    recipe_value = request.form.get("recipeTemp")  # Fetch value from the recipe slider
    meal_plan_value = request.form.get("mealPlanTemp")  # Fetch value from the meal plan slider

    if recipe_value and meal_plan_value:
        try:
            recipe_value = float(recipe_value)
            meal_plan_value = float(meal_plan_value)

            # Update the user's profile
            profile = UserProfile.query.filter_by(user_id=current_user.id).first()
            profile.recipe_temperature = recipe_value
            profile.meal_plan_temperature = meal_plan_value
            db.session.commit()
            flash("Temperatures updated successfully!", "success")
        except ValueError:
            flash("Invalid values provided for temperatures.", "danger")
    else:
        flash("Failed to update temperatures.", "danger")
    return redirect(url_for('views.profile'))


@views.context_processor
def inject_bug_report_form():
    return {'bug_report_form': BugReportForm()}


@views.route('/report_bug', methods=['POST'])
def report_bug():
    form = BugReportForm()
    if form.validate_on_submit():
        report = BugReport(description=form.description.data, steps=form.steps.data, user=current_user, timestamp=datetime.datetime.now())
        db.session.add(report)
        db.session.commit()
        flash('Thank you for your report. We will look into it.', 'success')
    print(form.errors)
    referrer = request.referrer
    return redirect(referrer)


@views.route('/view_reports')
def view_reports():
    reports = BugReport.query.all()
    return render_template('view_reports.html', reports=reports)

@views.route('/remove_report', methods=['POST'])
def remove_report():
    report_id = request.form.get('report_id')
    report = BugReport.query.get(report_id)
    if report:
        db.session.delete(report)
        db.session.commit()
        flash('Report removed successfully.', 'success')
    else:
        flash('Report not found.', 'danger')
    return redirect(url_for('views.view_reports'))


