# test_views.py 
import unittest
from mealmuse import create_app
from mealmuse.models import User, db, Pantry, ShoppingList, PantryItem, ShoppingListItem, Item
from werkzeug.security import generate_password_hash

class TestViewFunctions(unittest.TestCase):

    def setUp(self):
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        # Create a test user
        user = User(id=1, username="testuser", email="testuser@email.com", password=generate_password_hash("testpassword"))
        db.session.add(user)
        db.session.commit()
        db.session.close()  # Close the session after committing

        # Set up a test client
        self.client.post('/login', data={'username': 'testuser', 'password': 'testpassword'})  # Assuming there's a login route.

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # def test_index_get_request(self):
    #     response = self.client.get('/')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Welcome to My Meal Planning App!', response.data)

    # def test_index_post_request_valid_data(self):
    #     response = self.client.post('/', data={
    #         'user_message': 'Italian',
    #         'days': ['Monday', 'Tuesday'],
    #         'diet': ['Vegetarian']
    #     })
        
    #     # Depending on what you expect in the response, add assertions.
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Meal Plan', response.data)

    def test_add_item_to_pantry(self):
        # Use the test client to send a POST request to add an item to the pantry, then check if it was added
        response = self.client.post('/add_item', data={'name': 'Apple', 'quantity': '5', 'list_type': 'pantry'})
        self.assertEqual(response.status_code, 302)  # Assuming a redirect after successful addition
        added_item = PantryItem.query.filter_by(name='Apple').first()
        self.assertIsNotNone(added_item)
        self.assertEqual(added_item.quantity, 5)

    def test_edit_item_in_pantry(self):
        # Create the associated Item
        item = Item(name='Banana')
        db.session.add(item)
        db.session.commit()

        # Create a PantryItem associated with the created Item
        pantry_item = PantryItem(item=item, quantity=3)
        db.session.add(pantry_item)
        db.session.commit()

        # Use the client to edit the item's quantity
        response = self.client.post('/add_item', data={'name': 'Banana', 'quantity': '2', 'list_type': 'pantry'})
        self.assertEqual(response.status_code, 302)
        edited_item = PantryItem.query.filter_by(name='Banana').first()
        self.assertEqual(edited_item.quantity, 5)

    def test_remove_item_from_pantry(self):
        item = Item(name='Banana')
        db.session.add(item)
        db.session.commit()

        # Create a PantryItem associated with the created Item
        pantry_item = PantryItem(item=item, quantity=3)
        db.session.add(pantry_item)
        db.session.commit()

        # Use the client to remove the item from the pantry
        response = self.client.get(f'/remove_item/{item.id}')
        self.assertEqual(response.status_code, 302)
        removed_item = PantryItem.query.filter_by(name='Cherry').first()
        self.assertIsNone(removed_item)

    # def test_add_item_to_shopping_list(self):
    #     response = self.client.post('/add_item', data={'name': 'Pasta', 'quantity': '1', 'list_type': 'shopping_list'})
    #     self.assertEqual(response.status_code, 302)
    #     added_item = ShoppingListItem.query.filter_by(name='Pasta').first()
    #     self.assertIsNotNone(added_item)
    #     self.assertEqual(added_item.quantity, 1)

    # def test_edit_item_in_shopping_list(self):
    #     item = ShoppingListItem(name='Bread', quantity=2)
    #     db.session.add(item)
    #     db.session.commit()

    #     response = self.client.post('/add_item', data={'name': 'Bread', 'quantity': '3', 'list_type': 'shopping_list'})
    #     self.assertEqual(response.status_code, 302)
    #     edited_item = ShoppingListItem.query.filter_by(name='Bread').first()
    #     self.assertEqual(edited_item.quantity, 5)

    # def test_remove_item_from_shopping_list(self):
    #     item = ShoppingListItem(name='Milk', quantity=2)
    #     db.session.add(item)
    #     db.session.commit()

    #     response = self.client.get(f'/remove_item/{item.id}')
    #     self.assertEqual(response.status_code, 302)
    #     removed_item = ShoppingListItem.query.filter_by(name='Milk').first()
    #     self.assertIsNone(removed_item)

    #Add more test cases as necessary.

if __name__ == "__main__":
    unittest.main()
