import os
import json
import re
import openai
import time
from flask import current_app
from mealmuse import db, celery
from mealmuse.tasks import fetch_recipe_details_with_context, generate_meal_plan
from pint import UnitRegistry
import pint
from datetime import datetime, date
from .exceptions import InvalidOutputFormat
from .models import User, Pantry, Item, ShoppingList, MealPlan, Recipe, Day, Meal, RecipeItem, ShoppingListItem, PantryItem, UserProfile, Equipment, Allergy, Diet, users_recipes, recipes_mealplans, recipes_meals  # import the models if they are used in the utility functions
from test_data import meal_plan, recipes, shopping_list, meal_plan_biggus, meal_plan_output_gpt_4_v1, meal_plan_output_gpt_4_v2
from dotenv import load_dotenv

load_dotenv(".env")


# some custom unit conversions
ureg = UnitRegistry()
ureg.define('dash = 0.125 teaspoon = ds = dashes')
ureg.define('pinch = 0.0625 teaspoon = pn = pinches')
ureg.define('smidgen = 0.03125 teaspoon = sm')

# Meal Plan Generation; Generates a meal plan based on the user's preferences
def get_meal_plan(meal_plan_id, user_id):

    profile = UserProfile.query.filter_by(user_id=user_id).first()
    meal_plan_temp = profile.meal_plan_temperature if profile else 1
    db.session.remove()
    print("getting meal plan")

    generate_meal_plan.delay(meal_plan_id, user_id, meal_plan_temp)


# Meal Plan Generation; Generates a single recipe based on the user's preferences
def get_recipe(recipe_id, user_id):
    fetch_recipe_details_with_context.delay(recipe_id, user_id)


# Shopping list: removes all ingredients from a recipe from the user's shopping list
def remove_recipe_from_shopping_list(recipe_id, user):
    
    # Retrieve the recipe based on the given recipe ID
    recipe = db.session.get(Recipe, recipe_id)
    if not recipe:
        raise ValueError("Invalid recipe ID")

    # Retrieve the ingredients associated with the recipe
    recipe_items = db.session.query(RecipeItem).filter_by(recipe_id=recipe_id).all()

    # Check if the user has a shopping list. If not, there's nothing to remove.
    shopping_list = user.shopping_list
    if not shopping_list:
        return

    # Process each ingredient from the recipe
    for recipe_item in recipe_items:
        
        # Check if the item (as a ShoppingListItem) is present in the shopping list
        item_in_list = db.session.query(ShoppingListItem).join(ShoppingList).join(Item).filter(
            ShoppingList.id == shopping_list.id, 
            Item.name == recipe_item.item.name
        ).first()

        # If the item is present in the shopping list
        if item_in_list:
            try:
                # Create pint quantities for the quantity to be removed
                quantity_to_remove = recipe_item.quantity * ureg(recipe_item.unit)
            except pint.errors.UndefinedUnitError:
                # If there's a conversion error, use the quantity from the item in the shopping list
                quantity_to_remove = recipe_item.quantity
            
            # If the units match, just subtract the quantity
            if item_in_list.unit == recipe_item.unit:
                item_in_list.quantity -= round(recipe_item.quantity, 2)  # rounding to 2 decimal places
            else:
                # Try to convert the quantity to remove to the unit of the existing item
                try:
                    converted_quantity_to_remove = quantity_to_remove.to(item_in_list.unit)
                    item_in_list.quantity -= round(converted_quantity_to_remove.magnitude, 2)
                except pint.errors.UndefinedUnitError:
                    # If there's a conversion error, use the unit from the item in the shopping list
                    item_in_list.quantity -= round(quantity_to_remove, 2)

            # If the quantity becomes less than or equal to zero, remove the item from the shopping list
            if item_in_list.quantity <= 0:
                db.session.delete(item_in_list)

    # Commit the changes to the database
    db.session.commit()

    return shopping_list


def add_item_to_list(user, name, quantity, list_type, unit = None):
    # Get or create the general item in the Item table
    item = Item.query.filter_by(name=name).first()
    if not item:
        item = Item(name=name)
        db.session.add(item)
        db.session.commit()

    # if quantity is a string convert it to a float
    if isinstance(quantity, str):
        quantity = float(quantity)

    if list_type == 'pantry':
        pantry = Pantry.query.filter_by(user_id=user.id).first()
        existing_pantry_item = PantryItem.query.filter_by(item_id=item.id, pantry_id=pantry.id).first()
        if existing_pantry_item:
            #update the quantity
            existing_pantry_item = update_item_quantity(existing_pantry_item, quantity, unit)
         # If item is not present in the shopping list, add it
        else:
            pantry_item = PantryItem(item_id=item.id, pantry_id=pantry.id, quantity=quantity, unit=unit)
            db.session.add(pantry_item)
    
    elif list_type == 'shopping_list':
        shopping_list = ShoppingList.query.filter_by(user_id=user.id).first()
        # check if a shoppinglistitem table exists for 
        existing_list_item = ShoppingListItem.query.filter_by(item_id=item.id, shopping_list_id=shopping_list.id).first()
        if existing_list_item:
            # update the quantity
            existing_list_item = update_item_quantity(existing_list_item, quantity, unit)
         # If item is not present in the shopping list, add it
        else:
            shopping_list_item = ShoppingListItem(item_id=item.id, shopping_list_id=shopping_list.id, quantity=quantity, unit=unit)
            db.session.add(shopping_list_item)

    db.session.commit()


# Shopping list/ Pantry; add or remove quantity from existing item
def add_missing_or_all_items_to_shopping_list(user, recipe, action="add_missing"):
    pantry = Pantry.query.filter_by(user_id=user.id).first()
    pantry_items = {item.item.name: item for item in pantry.pantry_items} if pantry else {}
    
    for ingredient in recipe.recipe_items:
        # If the action is "add_missing", only add the item if it's not in the pantry
        if action == "add_missing" and ingredient.item.name in pantry_items:
            continue
        # If the action is "add_all", or the item was not in the pantry, add it to the shopping list
        unit = ingredient.unit
        ingredient_name = ingredient.item.name
        quantity = ingredient.quantity
        list_type = "shopping_list"

        add_item_to_list(user, ingredient_name, quantity, list_type, unit)


# Shopping list/ Pantry; add or remove quantity from existing item
def update_item_quantity(item, quantity, unit):

    #if item has no quantity, set it to 1
    if not item.quantity:
        item.quantity = 1
    # if no quantity is specified, increment by 1
    if not quantity:
        item.quantity += 1
        return item
    # if no units are specified, use the existing item's unit
    if not unit:
        unit = item.unit
    # if the item also has no units, just add the quantity
    if not item.unit:
        item.unit = unit
        item.quantity += round(quantity, 2)
        if item.quantity <= 0:
            db.session.delete(item)
            db.session.commit()
        return item or None
    # Create pint quantities for the existing item and the new quantity to be added
    try:
        additional_quantity = quantity * ureg(unit)
    except pint.errors.UndefinedUnitError:
        # If the unit is undefined, treat the units as matching
        unit = item.unit 
    except pint.errors.DimensionalityError:

        #TODO FIX THIS GARBAGE. Shouldn't happen much with revised prompts now though.
        # if we are trying to add cups to grams, just return the item
        return item

    # If the units match, just add the quantity
    if item.unit == unit:
        item.quantity += round(quantity, 2)  # round to 2 decimal places
    else:
        # Try to convert the new quantity to the unit of the existing item
        try:
            converted_additional_quantity = additional_quantity.to(item.unit)
            # Add the rounded converted magnitude to the existing quantity
            item.quantity += round(converted_additional_quantity.magnitude, 2) 

        # If there's a conversion error, leave the units as they are
        except pint.errors.UndefinedUnitError:
            # if we are trying to add basil leaves to grams of basil, just return the item unchanged
            print("Undefined unit error")
            return item
        # for dimensional errors don't change the quantity
        except pint.errors.DimensionalityError:
            # if we are trying to add cups to grams, just do nothing and return the item
            print(f"Dimensionality error, item: {item.item.name}")

            return item

    if item.quantity <= 0:
        db.session.delete(item) 
    return item or None


# Shopping list: removes all ingredients from a recipe from the user's pantry
def remove_recipe_items_from_pantry(user, recipe):
    pantry = Pantry.query.filter_by(user_id=user.id).first()
    pantry_items = {item.item.name: item for item in pantry.pantry_items} if pantry else {}
    
    for ingredient in recipe.recipe_items:
        # If the item is in the pantry, remove the quantity used in recipe
        if ingredient.item.name in pantry_items:
            pantry_item = pantry_items[ingredient.item.name]
            quantity = ingredient.quantity
            unit = ingredient.unit
            pantry_item = update_item_quantity(pantry_item, -quantity, unit)

    db.session.commit()


# # Shopping list: add one ingredient
# def add_ingredient_to_user_shopping_list(user, ingredient):
#     ingredient_name = ingredient['name']
#     quantity = ingredient['quantity']
#     unit = ingredient['unit']

#     # Check if the user has a shopping list, if not create one
#     shopping_list = user.shopping_list
#     if not shopping_list:
#         shopping_list = ShoppingList(user_id=user.id)
#         db.session.add(shopping_list)

#     # Check if the ingredient (as an Item) is already in the database, if not add it
#     item = db.session.query(Item).filter_by(name=ingredient_name).first()
#     if not item:
#         item = Item(name=ingredient_name)
#         db.session.add(item)

#     # Check if the ingredient (as a ShoppingListItem) is already in the user's shopping list
#     existing_list_item = db.session.query(ShoppingListItem).join(ShoppingList).join(Item).filter(Item.name == ingredient_name, ShoppingList.user_id == user.id).first()
#     if existing_list_item:
#         # Create pint quantities for the existing item and the new quantity to be added
#         try:
#             additional_quantity = quantity * ureg(unit)
#         except pint.errors.UndefinedUnitError:
#             # If the unit is undefined, treat the units as matching
#             additional_quantity = quantity 

#         # If the units match, just add the quantity
#         if existing_list_item.unit == unit:
#             existing_list_item.quantity += round(quantity, 2)  # round to 2 decimal places
#         else:
#             # Try to convert the new quantity to the unit of the existing item
#             try:
#                 converted_additional_quantity = additional_quantity.to(existing_list_item.unit)
#                 # Add the rounded converted magnitude to the existing quantity
#                 existing_list_item.quantity += round(converted_additional_quantity.magnitude, 2) 
#             # If there's a conversion error, leave the units in the shopping list as they are
#             except pint.errors.UndefinedUnitError:
#                 existing_list_item.quantity += round(additional_quantity, 2)
#      # If item is not present in the shopping list, add it
#     else:
#         shopping_list_item = ShoppingListItem(item_id=item.id, item=item, shopping_list_id=shopping_list.id, quantity=quantity, unit=unit)
#         db.session.add(shopping_list_item)
#     db.session.commit()

# # Shopping list; remove specified amount of one ingredient
# def remove_ingredient_from_user_shopping_list(user, ingredient, remove_entirely=False):
#     ingredient_name = ingredient['name']
#     quantity = ingredient['quantity']
#     unit = ingredient['unit']

#     # Check if the user has a shopping list. If not, there's nothing to remove
#     shopping_list = user.shopping_list
#     if not shopping_list:
#         return

#     # Check if the ingredient (as an Item) is in the database
#     item = db.session.query(Item).filter_by(name=ingredient_name).first()
#     if not item:
#         # If item is not in the database, it can't be in the shopping list
#         print(f"{ingredient_name} not found in the database")
#         return

#     # Check if the ingredient (as a ShoppingListItem) is in the user's shopping list
#     existing_list_item = db.session.query(ShoppingListItem).join(ShoppingList).join(Item).filter(Item.name == ingredient_name, ShoppingList.user_id == user.id).first()
    
#     if existing_list_item:
#         if remove_entirely:
#             db.session.delete(existing_list_item)
#             return
        
#         # Create pint quantities for the existing item and the quantity to be removed
#         try:
#             quantity_to_remove = quantity * ureg(unit)
#         except pint.errors.UndefinedUnitError:
#             # If there's an undefined unit, treat the units as matching
#             quantity_to_remove = quantity

#         # If the units match, just subtract the quantity
#         if existing_list_item.unit == unit:
#             existing_list_item.quantity -= round(quantity, 2)  # round to 2 decimal places
#         else:
#             # Try to convert the quantity to remove to the unit of the existing item
#             try:
#                 converted_quantity_to_remove = quantity_to_remove.to(existing_list_item.unit)
#                 existing_list_item.quantity -= round(converted_quantity_to_remove.magnitude, 2)
#             # If there's a conversion error, leave the units in the shopping list as they are
#             except pint.errors.UndefinedUnitError:
#                 existing_list_item.quantity -= round(quantity_to_remove, 2)

#         # If the quantity becomes less than or equal to zero, remove the item from the shopping list
#         if existing_list_item.quantity <= 0:
#             db.session.delete(existing_list_item)
#             db.session.commit()

# # Pantry; add one ingredient to the user's pantry
# def add_ingredient_to_user_pantry(user, ingredient):
#     ingredient_name = ingredient['name']
#     quantity = ingredient['quantity']
#     unit = ingredient['unit']
#     date_added = ingredient.get('date_added', None)
#     expiration_date = ingredient.get('expiration_date', None)

#     # Check if the user has a pantry, if not create one
#     pantry = user.pantry
#     if not pantry:
#         pantry = Pantry(user_id=user.id)
#         db.session.add(pantry)

#     # Check if the ingredient (as an Item) is already in the database, if not add it
#     item = db.session.query(Item).filter_by(name=ingredient_name).first()
#     if not item:
#         item = Item(name=ingredient_name)
#         db.session.add(item)

#     # Check if the ingredient (as a PantryItem) is already in the user's pantry
#     existing_pantry_item = db.session.query(PantryItem).join(Pantry).join(Item).filter(Item.name == ingredient_name, Pantry.user_id == user.id).first()
#     if existing_pantry_item:
#         # Create pint quantities for the existing item and the new quantity to be added
#         try:
#             additional_quantity = quantity * ureg(unit)
#         except pint.errors.UndefinedUnitError:
#             # If there's an undefined unit, treat the units as matching
#             additional_quantity = quantity
                
#         if existing_pantry_item.unit == unit:
#             existing_pantry_item.quantity += round(quantity, 2)  # round to 2 decimal places
#         else:
#             try:
#                 converted_additional_quantity = additional_quantity.to(existing_pantry_item.unit)
#                 existing_pantry_item.quantity += round(converted_additional_quantity.magnitude, 2) 
#             # If there's a conversion error, leave the units in the pantry as they are
#             except pint.errors.UndefinedUnitError:
#                 existing_pantry_item.quantity += round(additional_quantity, 2)
#     else:
#         pantry_item = PantryItem(item_id=item.id, pantry_id=pantry.id, quantity=quantity, unit=unit, date_added=date_added, expiration_date=expiration_date)
#         db.session.add(pantry_item)

#     db.session.commit()


# # Pantry; remove specified amount of one ingredient
# def remove_ingredient_from_user_pantry(user, ingredient, remove_entirely=False):
#     ingredient_name = ingredient['name']
#     quantity = ingredient['quantity']
#     unit = ingredient['unit']

#     pantry = user.pantry
#     if not pantry:
#         return

#     item = db.session.query(Item).filter_by(name=ingredient_name).first()
#     if not item:
#         return

#     existing_pantry_item = db.session.query(PantryItem).join(Pantry).join(Item).filter(Item.name == ingredient_name, Pantry.user_id == user.id).first()
    
#     if existing_pantry_item:
#         if remove_entirely:
#             db.session.delete(existing_pantry_item)
#             return
        
#        # Create pint quantities for the existing item and the quantity to be removed
#         try:
#             quantity_to_remove = quantity * ureg(unit)
#         except pint.errors.UndefinedUnitError:
#             # If there's an undefined unit, treat the units as matching
#             quantity_to_remove = quantity

#         if existing_pantry_item.unit == unit:
#             existing_pantry_item.quantity -= round(quantity, 2)
#         else:
#             try:
#                 converted_quantity_to_remove = quantity_to_remove.to(existing_pantry_item.unit)
#                 existing_pantry_item.quantity -= round(converted_quantity_to_remove.magnitude, 2)
#             # If there's a conversion error, leave the units in the pantry as they are
#             except pint.errors.UndefinedUnitError:
#                 existing_pantry_item.quantity -= round(quantity_to_remove, 2)

#         if existing_pantry_item.quantity <= 0:
#             db.session.delete(existing_pantry_item)

#     db.session.commit()


# Meal Plan save; initialize a blank meal plan for the user
def create_blank_meal_plan(user_id, preferred_cuisine):
    # Create a new meal plan
    new_meal_plan = MealPlan(date_created=datetime.now(), user_id=user_id)
    db.session.add(new_meal_plan)
    db.session.flush()  # Flush the session to assign an ID to the meal plan object
    # add the preferred cuisine to the meal plan
    new_meal_plan.cuisine_requests = preferred_cuisine
    # Commit changes to the database
    db.session.commit()
    return new_meal_plan


# Meal Plan save; adds a users selections for a single day to mealplan in database prior to meal plan generation
def save_day(meal_plan_id, current_day_datetime, meals_data):
    # Check if the day exists for the given meal_plan_id and current_day_datetime
    day = Day.query.filter_by(meal_plan_id=meal_plan_id, date=current_day_datetime).first()

    if not day:
        # Create a new Day
        day = Day(name=current_day_datetime.strftime("%A"), date=current_day_datetime, meal_plan_id=meal_plan_id)
        db.session.add(day)
        db.session.flush()  # Flush to get the generated id for the new Day
    # For each meal in meals_data, check if it exists for the day and update or create as necessary
    for meal_name, meal_info in meals_data.items():
        # Check if the meal exists for the day
        meal = Meal.query.filter_by(day_id=day.id, name=meal_name).first()

        if not meal:
            # Create a new Meal if it doesn't exist
            meal = Meal(name=meal_name, day_id=day.id)
            db.session.add(meal)
            db.session.flush()  # Flush to get the generated id for the new Meal

        # Update or set additional meal data (e.g. recipes, time, etc.)
        # Assuming columns exist in the Meal model for time, people, cuisine, type.
        meal.prep_time = meal_info.get('time')
        meal.num_people = meal_info.get('people')
        meal.cuisine = meal_info.get('cuisine')
        meal.type = meal_info.get('type')

    db.session.commit()
    return day

# Data retrieval and display; this function 
def get_meal_plan_details(user, meal_plan_id=None):
    if meal_plan_id:
        meal_plan = db.session.query(MealPlan).filter_by(id=meal_plan_id).first()
    else:
        # Fetch the most recent meal plan using the provided ID
        meal_plan = db.session.query(MealPlan).filter_by(user_id=user.id).order_by(MealPlan.date_created.desc()).first()

    if not meal_plan:
        return None  # or raise an exception

    # Dictionary to store the final result
    result = {
        "meal_plan_id": meal_plan.id,
        "description": meal_plan.description,
        "days": []
    }

    # Fetch days associated with the meal plan
    days = meal_plan.days

    for day in days:
        day_dict = {
            "day_id": day.id,
            "day_name": day.name,
            "date": day.date,
            "meals": []
        }

        # Fetch meals associated with the day
        meals = day.meal
        for meal in meals:
            meal_dict = {
                "meal_id": meal.id,
                "meal_name": meal.name,
                "recipes": []
            }

            # Fetch recipes associated with the meal
            recipes = meal.recipes
            for recipe in recipes:
                recipe_dict = {
                    "recipe_id": recipe.id,
                    "recipe_name": recipe.name,
                }
                meal_dict["recipes"].append(recipe_dict)
            
            day_dict["meals"].append(meal_dict)
        
        result["days"].append(day_dict)

    return result


# Data retrieval and display; this function retrieves the details of a list of recipes and returns it in a JSON with ingredients and cooking instructions
def get_recipe_details_by_ids(recipe_ids):
    # Fetch the recipes from the database using the given IDs
    recipes_db = db.session.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
    
    # If no recipes are found, return an empty list
    if not recipes_db:
        return []

    # List to hold the recipes
    recipes_list = []
    
    for recipe in recipes_db:
        recipe_data = {
            "recipe_id": recipe.id,
            "recipe_name": recipe.name,
            "instructions": recipe.instructions.split("\n") if recipe.instructions else [],
            "ingredients": []
        }
        
        # Fetch the ingredients associated with the recipe
        for recipe_item in recipe.recipe_items:
            ingredient_data = {
                "ingredient_id": recipe_item.item_id,
                "ingredient_name": recipe_item.item.name,
                "quantity": recipe_item.quantity,
                "unit": recipe_item.unit
            }
            recipe_data["ingredients"].append(ingredient_data)
        
        recipes_list.append(recipe_data)

    return recipes_list




# just a little helper function to go between the previous two  functions
def extract_recipe_ids(meal_plan_details):
    recipe_ids = []

    # Check if the response has an error key, if so, return an empty list
    if "error" in meal_plan_details:
        return recipe_ids

    # Traverse through days, meals, and recipes to extract recipe_ids
    for day in meal_plan_details["days"]:
        for meal in day["meals"]:
            for recipe in meal["recipes"]:
                recipe_ids.append(recipe["recipe_id"])

    return recipe_ids


# Data retrieval and display; this function retrieves a user profile.
def get_user_profile(user_id):
    # check if profile exists for user 
    if not UserProfile.query.filter_by(user_id=user_id).first():
        # if not, create a new profile
        new_profile = UserProfile(user_id=user_id)
        db.session.add(new_profile)
        db.session.commit()
    # return the profile
    return UserProfile.query.filter_by(user_id=user_id).first()

# Data retrieval and display; # check if meal_plan_id is in the session, if so pop it, check if it is not valid if so delete if from the database and the session
def check_for_incomplete_meal_plan(session):
    if 'meal_plan_id' in session:
        meal_plan_id = session.pop('meal_plan_id')
        meal_plan = db.session.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
        if not meal_plan:
            return
        if meal_plan.valid == False:
            db.session.delete(meal_plan)
            print("deleted meal plan")
            db.session.commit()
            return
        

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
