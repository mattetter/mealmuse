# test_recipe_model.py
import unittest
from mealmuse.app import app, db
from mealmuse.models import User, Recipe, Item, RecipeItem

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

    def test_recipe_item_association(self):
        # Create recipe
        r = Recipe(name='Test Recipe', instructions='Test instructions')
        db.session.add(r)

        # Create item
        i = Item(name='Test Item', quantity=1.0, unit='kg')
        db.session.add(i)

        # Associate item with recipe
        ri = RecipeItem(recipe_id=r.id, item_id=i.id, quantity_needed=0.5)
        db.session.add(ri)
        db.session.commit()

        # Check that the association was created
        r = Recipe.query.filter_by(name='Test Recipe').first()
        self.assertEqual(len(r.items), 1)
        self.assertEqual(r.items[0].name, 'Test Item')

        # Clean up
        db.session.delete(r)
        db.session.delete(i)
        db.session.commit()

# Run the tests with: python -m unittest test_recipe_model.py
