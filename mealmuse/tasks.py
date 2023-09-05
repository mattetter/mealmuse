import os
import re
import json
import openai
import time
from dotenv import load_dotenv

from mealmuse import db, celery
from mealmuse.models import User, Pantry, Item, ShoppingList, MealPlan, Recipe, Day, Meal, RecipeItem, ShoppingListItem, PantryItem, UserProfile, Equipment, Allergy, Diet, users_recipes, recipes_mealplans, recipes_meals  # import the models if they are used in the utility functions
from mealmuse.exceptions import InvalidOutputFormat  
from mealmuse.prompts  import recipes_prompt_35turbo_v1, meal_plan_system_prompt_gpt4_v2
from test_data import get_recipe, meal_plan_output_gpt_4_v2

load_dotenv(".env")

openai.api_key = os.getenv("OPENAI_API_KEY")
RECIPES_TASK = recipes_prompt_35turbo_v1
RECIPE_MODEL = "gpt-3.5-turbo-16k"

MEAL_PLAN_TASK = meal_plan_system_prompt_gpt4_v2
MEAL_PLAN_MODEL = "gpt-4"



def create_app_instance():
    from mealmuse import create_app  # Adjust this import to your actual function
    app = create_app('config.DevelopmentConfig') 
    return app


@celery.task
def generate_meal_plan(meal_plan_id, user_id):
    app = create_app_instance()
    with app.app_context():
        try:

            meal_plan = MealPlan.query.filter_by(id=meal_plan_id).first()
            user = User.query.filter_by(id=user_id).first()

            # get meal plan from openai
            meal_plan_output = fetch_meal_plan_from_api(meal_plan, user)

            # fake api call for testing
            # meal_plan_output = meal_plan_output_gpt_4_v2
            
            # save generated meal plan with user selections to database
            meal_plan_id = save_meal_plan_output(meal_plan_output, meal_plan, user)
            # fetch recipe details in parallel
            
            fetch_recipe_details_with_context(meal_plan_id)

        except Exception as e:
            db.session.rollback()
            print(f"Error occurred: {e}")
            db.session.remove()
            raise
        return meal_plan_id
    

# Meal Plan generation; wrap the recipe api call in a function to be used in parallel
def fetch_recipe_details_with_context(meal_plan_id):
    app = create_app_instance()
    with app.app_context():
        try:
            meal_plan = MealPlan.query.filter_by(id=meal_plan_id).first()
            result = [fetch_recipe_details.delay(recipe.id) for recipe in meal_plan.recipes]
        except Exception as e:
            db.session.rollback()
            print(f"Error occurred: {e}")
            db.session.remove()
            raise
        return result


# # Meal Plan generation: generate a single recipe
# @celery.task
# def generate_recipe(recipe_id, meal_id = None):
#     app = create_app_instance()
#     with app.app_context():
#         try:
#             recipe = Recipe.query.filter_by(id=recipe_id).first()
#             recipe_output = fetch_recipe_details(recipe_id)
#             # fake api call for testing
#             # recipe_output = get_recipe(recipe.name)
#             recipe_id = process_recipe_output(recipe_output, recipe_id)
#         except Exception as e:
#             db.session.rollback()
#             print(f"Error occurred: {e}")
#             db.session.remove()
#             raise
#         return recipe_id


# Meal Plan generation; process the user input to create a user prompt in the expected format
def create_meal_plan_user_prompt(user, meal_plan):
    
    # Placeholder for the result in json format
    result = {}

    # get the user's pantry items
    pantry_items = []
    pantry = user.pantry
    if pantry:
        pantry_items = [item.item.name for item in pantry.pantry_items]

    # check if user has any equipment
    equipment = []
    if user.equipment:
        equipment = [equipment.name for equipment in user.equipment]

    # check if user has any allergies
    allergy = []
    if user.allergies:
        allergy = [allergy.name for allergy in user.allergies]

    # check if user has any dietary restrictions
    diet = []
    if user.diets:
        diet = [diet.name for diet in user.diets]

    # get the user's proficiency
    user_profile = UserProfile.query.filter_by(user_id=user.id).first()
    if user_profile:
        proficiency = user_profile.proficiency
    else:
        # create a profile and set proficiency to intermediate
        user_profile = UserProfile(user_id=user.id, proficiency="Beginner")
        db.session.add(user_profile)
        db.session.commit()
        proficiency = user_profile.proficiency

    # get the pantry use preference and budget jand leftover management for this meal plan
    pantry_usage_preference = meal_plan.pantry_use
    budget = meal_plan.budget
    leftovers = meal_plan.leftovers
    cuisine = meal_plan.cuisine_requests



    # Build the json object
    general = {
        "allergies": allergy,
        "cuisine and user requests": cuisine if cuisine else 'any', # Defaulting to 'Any' if not provided
        "dietary restrictions": diet if diet else 'no restrictions', # Defaulting to 'No restrictions' if not provided
        "pantry_items": pantry_items,
        "pantry_usage_preference": pantry_usage_preference,
        # "calorie_range": calorie_range,
        # "macronutrients": {
        #     "carbs": 45,    # You can replace with actual data if available
        #     "protein": 25,  # You can replace with actual data if available
        #     "fats": 30      # You can replace with actual data if available
        # },
        "equipment": equipment,
        "culinary_skill": proficiency,
        "budget": budget, 
        "meal_diversity": "high", #TO DO: meal_diversity,
        "leftover_management": leftovers,
        "description": "please generate"
    }

    daily = {}

    # meal_plan.days fetches the days associated with this meal plan
    for day in meal_plan.days:
        daily[day.name] = []
        for meal in day.meal:
            meal_details = {
                "name": meal.name,
                "prep_time": meal.prep_time,
                "num_people": meal.num_people,
                "cuisine": meal.cuisine,
                "type": meal.type
            }
            daily[day.name].append(meal_details)
    
    # Compile the result
    result = {
            "general": general,
            "daily": daily
        }

    return json.dumps(result)


# Meal Plan generation; the api call to get a meal plan
def fetch_meal_plan_from_api(meal_plan, user):
    
    # Create the user prompt
    user_prompt = create_meal_plan_user_prompt(user, meal_plan)
    response = openai.ChatCompletion.create(
        model=MEAL_PLAN_MODEL,
        messages=[
            {"role": "system", "content": MEAL_PLAN_TASK},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=3000,
        temperature=1,
    )
    meal_plan_text = response.choices[0].message['content']

    try:
        # Attempt to parse the output as JSON
        meal_plan_json = json.loads(meal_plan_text)
    except json.JSONDecodeError:
        # If the output is not JSON, raise InvalidOutputFormat
        raise InvalidOutputFormat("Output is not valid JSON")
        
    return meal_plan_json
    # return meal_plan_output_gpt_4_v2


# Meal Plan Save: takes the output from the meal plan api call and saves it to the database
def save_meal_plan_output(meal_plan_json, meal_plan, user):

    # save the description to the meal plan
    meal_plan.description = meal_plan_json['description']

    for day_name, day_data in meal_plan_json['days'].items():
        # Find the day object corresponding to the day name (like 'Tuesday' or 'Wednesday')
        day_obj = Day.query.filter_by(name=day_name, meal_plan_id=meal_plan.id).first()
        if not day_obj:
            continue
        
        for meal_name, meal_data in day_data.items():
            # Find the meal object corresponding to the meal name (like 'Breakfast', 'Lunch'...)
            meal_obj = Meal.query.filter_by(name=meal_name, day_id=day_obj.id).first()
            if not meal_obj:
                continue
            
            # Extract recipe data
            recipe_data = meal_data['recipe']
            new_recipe = Recipe(
                name=recipe_data['name'],
                cost=recipe_data['cost_in_dollars'],
                time=recipe_data['time_required'],
                serves=recipe_data['serves'],
                cuisine=meal_obj.cuisine,
                num_ingredients=recipe_data['number_of_ingredients']
            )
            
            # Add the new recipe to the database
            db.session.add(new_recipe)
            db.session.flush()  # To get the ID for the new recipe after adding it
            # Associate the new recipe with the meal object
            meal_obj.recipes.append(new_recipe)

            # Associate the new recipe with the meal plan
            meal_plan.recipes.append(new_recipe)

            # Associate the new recipe with the user
            user.recipes.append(new_recipe)

            # Save ingredients to the RecipeItem model
            for ingredient in recipe_data['ingredients_from_pantry']:
                # Here we're assuming each ingredient is a new unique item. If not, 
                # you'd need to check the database for existing items before creating a new one.
                item = Item(name=ingredient)
                db.session.add(item)
                db.session.flush()  # To get the ID for the new item after adding it

                # Create a RecipeItem instance
                recipe_item = RecipeItem(recipe_id=new_recipe.id, item_id=item.id)
                db.session.add(recipe_item)
            db.session.commit()

    return meal_plan.id


# Meal Plan generation; the api call to get a recipe
@celery.task
def fetch_recipe_details(recipe_id):
    recipe = db.session.query(Recipe).filter_by(id=recipe_id).first()
    
    retries = 2
    recipe_user_prompt = create_recipe_user_prompt(recipe)
    recipe_name = recipe.name
    for _ in range(retries):
        response = openai.ChatCompletion.create(
            model=RECIPE_MODEL,
            messages=[
                {"role": "system", "content": RECIPES_TASK},
                {"role": "user", "content": recipe_user_prompt},
            ],
            max_tokens=2000,
            temperature=1,
        )
        recipes_text = response.choices[0].message['content']
        # fake the api call for testing
        # recipes_text = get_recipe(recipe.name)
        try:
            return {recipe.name: process_recipe_output(recipes_text, recipe_id)}
        except InvalidOutputFormat as e:
            print(f"Error processing recipe for {recipe_name}: {e}. Retrying...")
            
    raise Exception(f"Failed to get a valid response for {recipe_name} after {retries} attempts.")


# Meal Plan generation; Pull info from db to create a user prompt for a recipe
def create_recipe_user_prompt(recipe):
    # Placeholder for the result in json format
    result = {}

    # get the recipe specific details
    name = recipe.name
    cost = recipe.cost
    time = recipe.time
    serves = recipe.serves
    cuisine = recipe.cuisine
    num_ingredients = recipe.num_ingredients

    # get the recipe's ingredients
    ingredients = []
    for recipe_item in recipe.recipe_items:
        ingredients.append(recipe_item.item.name)

    # create text file with description and the above details
    result = {
        "Please create a recipe with the following details:" : {
        "name": name,
        "cost": cost,
        "total time to make": time,
        "serves": serves,
        "total number of ingredients": num_ingredients,
        "ingredients from pantry to include": ingredients,
        "cuisine or user requests": cuisine
    }}

    return json.dumps(result)


# Meal Plan Save; takes the output from the recipe api call and saves it to the database
def process_recipe_output(data, recipe_id):

    recipe = db.session.query(Recipe).filter_by(id=recipe_id).first()
    
    # clear ingredients used to generate recipe in favor of ones with quantities
    for item in recipe.recipe_items:
        db.session.delete(item)
    db.session.commit()

    # Placeholder for the processed data
    result = {}
    # If data is a string, try to deserialize it as JSON
    if isinstance(data, str):
        try:
            data = load_json_with_fractions(data)
        except json.JSONDecodeError:
            print(f"invalid json: {data}")
            raise InvalidOutputFormat("Provided string is not valid JSON")

    # Check if the data has 'recipe' key format
    if "recipe" not in data:
        print(f"no recipe: {data}")
        raise InvalidOutputFormat("Output does not have a 'recipe' key")
    
    details = data["recipe"]

    # Validating ingredients
    ingredients = details.get('ingredients', [])
    if not ingredients or not isinstance(ingredients, list):
        print(f"no ingredients: {ingredients}")
        raise InvalidOutputFormat("Missing or invalid ingredients for recipe")

    # Validate and save each ingredient
    for ingredient in ingredients:
        if not all(key in ingredient for key in ['name', 'quantity', 'unit']):
            print(f"invalid ingredient: {ingredient}")
            raise InvalidOutputFormat("Invalid ingredient format for recipe")
        
        # Check if the ingredient already exists in the database
        existing_item = db.session.query(Item).filter(Item.name == ingredient['name']).first()
        if existing_item:
            item = existing_item
        else:
            item = Item(name=ingredient['name'])
            db.session.add(item)
            db.session.flush()
        # Create a RecipeItem instance
        recipe_item = RecipeItem(recipe_id=recipe.id, item_id=item.id, quantity=ingredient['quantity'], unit=ingredient['unit'])
        db.session.add(recipe_item)

    # Validating cooking instructions
    instructions = details.get('cooking_instructions', [])
    if not instructions or not isinstance(instructions, list):
        print(f"no instructions: {instructions}")
        raise InvalidOutputFormat("Missing or invalid cooking instructions for recipe")

    # Validate each instruction and save to the database
    for idx, instruction in enumerate(instructions, 1):
        if not instruction.startswith(f"Step {idx}:"):
            print(f"invalid step: {instruction}")
            raise InvalidOutputFormat("Invalid step format for recipe")
    
    # add instructions to recipe
    recipe.instructions = "\n".join(instructions)

    db.session.commit()
    # give the celery worker some time to finish the transaction
    return recipe_id



def fraction_to_decimal(match):
    """Converts a fraction to its decimal representation."""
    num, den = map(int, match.group(0).split('/'))
    return str(num / den)

def preprocess_json_string(s):
    """Replaces fractions with their decimal equivalents in a string."""
    return re.sub(r'\b\d+/\d+\b', fraction_to_decimal, s)

def load_json_with_fractions(s):
    """Loads a JSON string, even if it contains fractions."""
    preprocessed_string = preprocess_json_string(s)
    return json.loads(preprocessed_string)


# from celery.signals import worker_process_init

# @worker_process_init.connect
# def on_worker_init(*args, **kwargs):
#     warmup.apply_async()



# @celery.task
# def warmup():
#     # Perform some simple database queries
#     some_query = db.session.query(Recipe).limit(1).all()
#     another_query = db.session.query().limit(1).all()

#     # Close the session
#     db.session.remove()
