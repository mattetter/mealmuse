# views.py is the file that contains all the routes for our application.
from . import login_manager, db
import json
import datetime
from datetime import date
from flask import Blueprint
from flask import flash, redirect, render_template, request, session, url_for, current_app, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from .forms import PantryItemForm, RegistrationForm, LoginForm  # import the forms
from .models import User, Pantry, Item, ShoppingList, MealPlan, Recipe, PantryItem, ShoppingListItem, Meal, Day, Diet, Allergy, UserProfile  # import the models
from .utils import get_meal_plan, get_meal_plan_details, get_recipe_details_by_ids, extract_recipe_ids, get_user_profile, create_blank_meal_plan, check_for_incomplete_meal_plan, save_day # import the utility functions
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
    return redirect(url_for('login'))


@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmation')

        if not username or not password or not confirm_password:
            flash('All fields are required.', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match.', 'danger')
        else:
            hashed_password = generate_password_hash(password, method='sha256')
            new_user = User(username=username, email="test@test.test", password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('You have been registered successfully.', 'success')
            return redirect(url_for('login'))
        
    return render_template('register.html')


#automatically create tables and log in test user
@views.before_request
def before_request():

    # # Create the database tables for our data models
    # db.create_all()
    # If there's no user logged in
    if not current_user.is_authenticated:

        # check if the test user exists
        user = User.query.filter_by(username="testuser").first()
        if not user:
            # Create a test user
            user = User(id=1, username="testuser", email="testuser@email.com", password=generate_password_hash("testpassword"))
            db.session.add(user)
            db.session.commit()

        # log the user in
        login_user(user)



@views.route('/pantry_and_list')
@login_required
def pantry_and_list():
    # Assume we have a current_user object that represents the logged-in user
    user = User.query.get(current_user.id)

    # If the user doesn't have a pantry or a shopping list, create them
    if not user.pantry:
        pantry = Pantry(user=user)
        db.session.add(pantry)
    
    if not user.shopping_list:
        shopping_list = ShoppingList(user=user)
        db.session.add(shopping_list)

    db.session.commit()

    # Fetch pantry and shopping list items for the current user from the database
    pantry_items = user.pantry.pantry_items if user.pantry else []
    shopping_list_items = user.shopping_list.shopping_list_items if user.shopping_list else []

    return render_template('pantry_and_list.html', pantry_items=pantry_items, shopping_list_items=shopping_list_items)

@views.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity') or 1
        list_type = request.form.get('list_type')
        
        # Get or create the general item in the Item table
        item = Item.query.filter_by(name=name).first()
        if not item:
            item = Item(name=name)
            db.session.add(item)
        
        if list_type == 'pantry':
            pantry = Pantry.query.filter_by(user_id=current_user.id).first()
            pantry_item = PantryItem.query.filter_by(item_id=item.id, pantry_id=pantry.id).first()
            if pantry_item:
                pantry_item.quantity += float(quantity)
            else:
                pantry_item = PantryItem(item_id=item.id, pantry_id=pantry.id, quantity=quantity)
                db.session.add(pantry_item)
        elif list_type == 'shopping_list':
            shopping_list = ShoppingList.query.filter_by(user_id=current_user.id).first()
            shopping_list_item = ShoppingListItem.query.filter_by(item_id=item.id, shopping_list_id=shopping_list.id).first()
            if shopping_list_item:
                shopping_list_item.quantity += float(quantity)
            else:
                shopping_list_item = ShoppingListItem(item_id=item.id, shopping_list_id=shopping_list.id, quantity=quantity)
                db.session.add(shopping_list_item)

        db.session.commit()
        
        return redirect(url_for('views.pantry_and_list'))

    return render_template('views.pantry_and_list.html')



# Edit an existing item in the pantry or shopping list
@views.route('/remove_item/<string:list_type>/<int:item_id>')
def remove_item(list_type, item_id):
    if list_type == "pantry":
        item = PantryItem.query.get(item_id)
    elif list_type == "shopping_list":
        item = ShoppingListItem.query.get(item_id)
    else:
        flash("Invalid list type!")
        return redirect(url_for('pantry_and_list'))

    if item:
        db.session.delete(item)
        db.session.commit()
    else:
        flash("Item not found!")
    
    return redirect(url_for('views.pantry_and_list'))


# the homescreen
@views.route("/", methods=("GET", "POST"))
@login_required
def index():
    if 'redirect_count' in session:
        del session['redirect_count']
    if request.method == "POST":
        user_message = request.form["user_message"]   # free form Cuisine
        selected_days = request.form.getlist('days')  # get the list of selected days
        selected_days_str = ', '.join(selected_days)
        selected_diet = request.form.getlist('diet')  # get the list of selected dietary preferences
        selected_diet_str = ', '.join(selected_diet)

        # error handling for bad api outputs
        max_retries = 2
        retries = 0
        while retries <= max_retries:
            try:
                # Call the get_meal_plan function to generate a meal plan, recipes and shopping list
                try:
                     meal_plan_obj = get_meal_plan(user_message, selected_days_str, selected_diet_str, current_user)
                except Exception as e:
                    raise e

                # fetch the most recent meal plan
                meal_plan_to_display = get_meal_plan_details(current_user, meal_plan_obj.id)
                # get recipe details for the recipes in the meal plan
                recipes_to_display = get_recipe_details_by_ids(extract_recipe_ids(meal_plan_to_display))
                return render_template('index.html', meal_plan=meal_plan_to_display, recipes=recipes_to_display)

            except InvalidOutputFormat as e:
                print(f"Error: {e}")
                retries += 1
                if retries > max_retries:
                    return render_template("index.html", error_message="An error occurred while generating your meal plan. Please try again.")

            except Exception as e:
                print(f"Error: {e}")
                return render_template("index.html", error_message="An error occurred while generating your meal plan. Please try again.")

        return render_template("index.html", error_message="An error occurred while generating your meal plan. Please try again.")

    else:  # GET request
       # Initialize both to None or appropriate defaults
        meal_plan_to_display = None
        recipes_to_display = None

        # Fetch the most recent meal plan
        meal_plan_to_display = get_meal_plan_details(current_user)
        # Get recipe details for the recipes in the meal plan

        return render_template('index.html', meal_plan=meal_plan_to_display, recipes=recipes_to_display, datetime=datetime)


# Meal Plan: main route
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

        return redirect(url_for('views.budget_selection'))

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

            # Cleanup session
            del session['selected_days']
            del session['current_day_index']
            

            return redirect(url_for('views.meal_plan_loading'))
    
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
    return render_template('select_items.html', current_day=formatted_day, datetime=datetime)


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

    # set the meal_plan to valid
    meal_plan.valid = True
    # generate the meal_plan with the current app object
    meal_plan = get_meal_plan(meal_plan.id, user.id)

    return jsonify(status="success", message="Meal plan generated!")


# Displays a given recipe in the meal plan page
@views.route('/recipe/<int:recipe_id>', methods=['GET'])
def recipe_in_meal_plan_page(recipe_id):
    # Fetch recipe details using recipe_id from the database.
    recipe = db.session.query(Recipe).filter_by(id=recipe_id).first()
    if not recipe:
        flash('Recipe not found!', 'error')
        return redirect(url_for('views.meal_plan'))

    # Render the recipe details page.
    return render_template('recipe.html', recipe=recipe)


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

        # Fetch proficiency and family size for the user
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    current_proficiency = profile.proficiency if profile else None
    current_family_size = profile.family_size if profile else None
    print (current_proficiency)
    return render_template('profile.html', allergies=allergies, dietary_restrictions=dietary_restrictions, current_proficiency=current_proficiency, current_family_size=current_family_size)


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
