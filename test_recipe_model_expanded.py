import unittest
from datetime import date
from mealmuse.app import app, db
from mealmuse.models import User, Recipe, Item, Meal, Day, MealPlan, Pantry, ShoppingList, PantryItem, ShoppingListItem, RecipeItem

class RecipeModelCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfig')
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_recipe_creation(self):
        # Create recipe
        r = Recipe(name='Test Recipe', instructions='Test instructions')
        db.session.add(r)
        db.session.commit()

        # Retrieve recipe by name
        r = Recipe.query.filter_by(name='Test Recipe').first()
        self.assertIsNotNone(r)

        # Clean up
        db.session.delete(r)
        db.session.commit()

    def test_recipe_meal_association(self):
        # Create recipe
        r = Recipe(name='Test Recipe', instructions='Test instructions')
        db.session.add(r)

        # Create meal
        m = Meal(name='Test Meal')
        db.session.add(m)

        # Associate recipe with meal
        m.recipes.append(r)
        
        # Create day
        d = Day(name='Test Day')
        db.session.add(d)
        db.session.commit()

        # Associate meal with day
        m.day_id = d.id
        db.session.commit()


    def test_recipe_mealplan_association(self):
        # Create recipe
        r = Recipe(name='Test Recipe', instructions='Test instructions')
        db.session.add(r)

        # Create mealplan
        mp = MealPlan(date=date(2023, 8, 1))
        db.session.add(mp)

        # Associate recipe with mealplan
        mp.recipes.append(r)
        db.session.commit()

        # Check that the association was created
        mp = MealPlan.query.filter_by(date=date(2023, 8, 1)).first()
        self.assertEqual(len(mp.recipes), 1)
        self.assertEqual(mp.recipes[0].name, 'Test Recipe')

        # Clean up
        db.session.delete(r)
        mp.recipes = []  # Clear relationships
        db.session.delete(mp)
        db.session.commit()

    def test_pantry(self):
        # Create user
        u = User(username='testuser', email='test@example.com', password='testpassword')
        db.session.add(u)
        db.session.commit()

        # Create an item
        item = Item(name='ExampleItem')
        db.session.add(item)
        db.session.flush()  # flush to ensure item.id is accessible in the next step

        # Create pantry for user and associate the item
        pantry = Pantry(user_id=u.id)
        pantry_item = PantryItem(item_id=item.id, quantity=5, unit="kg")
        pantry.pantry_items.append(pantry_item)
        db.session.add(pantry)
        db.session.commit()

        # Check that the pantry was created
        u = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(u.pantry)
        self.assertEqual(len(u.pantry.pantry_items), 1)

        # Clean up
        db.session.delete(u)
        db.session.delete(item)
        db.session.commit()

    def test_shoppinglist(self):
        # Create user
        u = User(username='testuser', email='test@example.com', password='testpassword')
        db.session.add(u)
        db.session.commit()

        # Create 10 items and add them to the shopping list for the user
        shopping_list = ShoppingList(user_id=u.id)
        for i in range(1, 11):
            item = Item(name=f'item{i}')
            shopping_list_item = ShoppingListItem(item_id=item.id, quantity=i, unit="pcs")
            shopping_list.shopping_list_items.append(shopping_list_item)
            db.session.add(item)
        db.session.add(shopping_list)
        db.session.commit()

        # Check that the shopping list was created with 10 items
        u = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(u.shopping_list)
        self.assertEqual(len(u.shopping_list.shopping_list_items), 10)

        # Clean up
        db.session.delete(u)
        for item in Item.query.all():
            db.session.delete(item)
        db.session.commit()


    def test_user_recipe_association(self):
        u = User(username='testuser', email='test@example.com', password='testpassword')
        r = Recipe(name='testrecipe', instructions='testinstructions')
        u.recipes.append(r)

        db.session.add(u)
        db.session.commit()

        self.assertTrue(r in u.recipes)

    def test_meal_recipe_association(self):
        meal = Meal(name='dinner')
        recipe = Recipe(name='testrecipe', instructions='testinstructions')
        meal.recipes.append(recipe)

        db.session.add(meal)
        
        # Create day
        d = Day(name='Test Day 2')
        db.session.add(d)
        db.session.commit()

        # Associate meal with day
        meal.day_id = d.id
        db.session.commit()


    def test_recipe_crud(self):
        # Create (C)
        r = Recipe(name='CRUD Recipe', instructions='Test instructions')
        db.session.add(r)
        db.session.commit()

        # Read (R)
        r = Recipe.query.filter_by(name='CRUD Recipe').first()
        self.assertIsNotNone(r)

        # Update (U)
        r.name = 'Updated CRUD Recipe'
        db.session.commit()
        r = Recipe.query.filter_by(name='Updated CRUD Recipe').first()
        self.assertIsNotNone(r)

        # Delete (D)
        db.session.delete(r)
        db.session.commit()
        r = Recipe.query.filter_by(name='Updated CRUD Recipe').first()
        self.assertIsNone(r)


# Run the tests with: python -m unittest test_recipe_model_expanded.py
