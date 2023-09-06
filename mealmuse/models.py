from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime

db = SQLAlchemy()

# Models

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    family_size = db.Column(db.Integer, default=1)
    proficiency = db.Column(db.String(80), default="Beginner")
    budget = db.Column(db.Integer, default=150)
    pantry_use = db.Column(db.String(200), default = "Use best judgment regarding usage of recipe ingredients in pantry vs items not in pantry")
    leftovers = db.Column(db.String, default="I'm okay with leftovers, but prefer variety")
    cuisine_requests = db.Column(db.String(200), default="Any")
    meal_diversity = db.Column(db.Float, default=0.5)
    calorie_range = db.Column(db.String(80), default="2000-2500")
    protein_range = db.Column(db.String(80), default="50-100")
    fat_range = db.Column(db.String(80), default="50-100")
    carbs_range = db.Column(db.String(80), default="50-100")
    fiber = db.Column(db.String(80), default="50-100")
    sugar = db.Column(db.String(80), default="50-100")
    sodium = db.Column(db.String(80), default="50-100")
    cholesterol = db.Column(db.String(80), default="50-100")



class Allergy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
 
class Diet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    instructions = db.Column(db.String(1500))
    cuisine = db.Column(db.String(300))
    rating = db.Column(db.Integer)
    cost = db.Column(db.Integer)
    time = db.Column(db.Integer)
    serves = db.Column(db.Integer)
    tags = db.Column(db.String(200))
    num_ingredients = db.Column(db.Integer)

class MealPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500))
    date_created = db.Column(db.DateTime, nullable=False)
    valid = db.Column(db.Boolean, default=False)
    budget = db.Column(db.Integer, default=150)
    pantry_use = db.Column(db.String(200), default = "Use best judgment regarding usage of recipe ingredients in pantry vs items not in pantry")
    leftovers = db.Column(db.String, default="I'm okay with leftovers, but prefer variety")
    cuisine_requests = db.Column(db.String(200), default="Any")
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)

class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date)
    meal_plan_id = db.Column(db.Integer, ForeignKey('meal_plan.id'), nullable=False)

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    day_id = db.Column(db.Integer, ForeignKey('day.id'), nullable=False)
    prep_time = db.Column(db.Integer)
    num_people = db.Column(db.Integer)
    cuisine = db.Column(db.String(100))
    type = db.Column(db.String(100))

class Pantry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)

class ShoppingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False) 
    recipe_id = db.Column(db.Integer, ForeignKey('recipe.id'), nullable=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class PantryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pantry_id = db.Column(db.Integer, ForeignKey('pantry.id'))
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(80))
    date_added = db.Column(DateTime)
    expiration_date = db.Column(DateTime)
    item_id = db.Column(db.Integer, ForeignKey('item.id'), nullable=False)
    item = db.relationship('Item', backref='pantry_items', lazy=True)

class ShoppingListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shopping_list_id = db.Column(db.Integer, ForeignKey('shopping_list.id'))
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(80))
    recipe_id = db.Column(db.Integer, ForeignKey('recipe.id'), nullable=True)
    item_id = db.Column(db.Integer, ForeignKey('item.id'), nullable=False)
    item = db.relationship('Item', backref='shopping_list_items', lazy=True)

class RecipeItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, ForeignKey('recipe.id'), nullable=False)
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(80))
    item_id = db.Column(db.Integer, ForeignKey('item.id'), nullable=False)
    item = db.relationship('Item', backref='recipe_items', lazy=True)



# association tables
users_recipes = db.Table('users_recipes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
)

recipes_meals = db.Table('recipes_meals',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
    db.Column('meal_id', db.Integer, db.ForeignKey('meal.id'), primary_key=True)
)

mealplans_users = db.Table('mealplans_users',
    db.Column('meal_plan_id', db.Integer, db.ForeignKey('meal_plan.id'), primary_key=True), 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

recipes_mealplans = db.Table('recipes_mealplans',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'), primary_key=True),
    db.Column('meal_plan_id', db.Integer, db.ForeignKey('meal_plan.id'), primary_key=True)  # changed 'mealplan' to 'meal_plan'
)

user_allergies = db.Table('user_allergies',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('allergy_id', db.Integer, db.ForeignKey('allergy.id'), primary_key=True)
)

user_diets = db.Table('user_diets',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('diet_id', db.Integer, db.ForeignKey('diet.id'), primary_key=True)
)

user_equipment = db.Table('user_equipment',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('equipment_id', db.Integer, db.ForeignKey('equipment.id'), primary_key=True)
)

# Finalize relationships

User.pantry = db.relationship('Pantry', backref='user', uselist=False, cascade="all, delete-orphan")
User.shopping_list = db.relationship('ShoppingList', backref='user', uselist=False, cascade="all, delete-orphan")

User.recipes = db.relationship('Recipe', secondary=users_recipes, lazy='subquery', 
    backref=db.backref('users', lazy=True))

User.allergies = db.relationship('Allergy', secondary=user_allergies, lazy='subquery',
    backref=db.backref('users', lazy=True))

User.diets = db.relationship('Diet', secondary=user_diets, lazy='subquery',
    backref=db.backref('users', lazy=True))

User.equipment = db.relationship('Equipment', secondary=user_equipment, lazy='subquery',
    backref=db.backref('users', lazy=True))

Meal.recipes = db.relationship('Recipe', secondary=recipes_meals, lazy='subquery',
    backref=db.backref('meals', lazy=True))

MealPlan.recipes = db.relationship('Recipe', secondary=recipes_mealplans, lazy='subquery',
    backref=db.backref('meal_plans', lazy=True))



# backrefs
Pantry.pantry_items = db.relationship('PantryItem', backref='pantry', lazy=True, cascade="all, delete-orphan")
ShoppingList.shopping_list_items = db.relationship('ShoppingListItem', backref='shopping_list', lazy=True, cascade="all, delete-orphan")
Recipe.recipe_items = db.relationship('RecipeItem', backref='recipe', lazy=True, cascade="all, delete-orphan")
MealPlan.days = db.relationship('Day', backref='meal_plan', lazy=True, cascade="all, delete-orphan")
Day.meal = db.relationship('Meal', backref='day', lazy=True, cascade="all, delete-orphan")
User.meal_plans = db.relationship('MealPlan', backref='user', lazy=True, cascade="all, delete-orphan")
