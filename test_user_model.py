# test_user_model.py
import unittest
from mealmuse.app import app, db
from mealmuse.models import User
from werkzeug.security import generate_password_hash

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfig')
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_retrieval(self):
        # Create user
        u = User(username='john', email='john@example.com', password='password')
        db.session.add(u)
        db.session.commit()

        # Retrieve user by username
        u = User.query.filter_by(username='john').first()
        self.assertIsNotNone(u)

        # Clean up
        db.session.delete(u)
        db.session.commit()

    def test_user_update(self):
        # Create user
        u = User(username='john', email='john@example.com', password='password')
        db.session.add(u)
        db.session.commit()

        # Update user's email
        u = User.query.filter_by(username='john').first()
        u.email = 'new_john@example.com'
        db.session.commit()
        
        u = User.query.filter_by(username='john').first()
        self.assertEqual(u.email, 'new_john@example.com')
        print(u.id)

        # Clean up
        db.session.delete(u)
        db.session.commit()

    def test_user_deletion(self):
        # Create user
        u = User(username='john', email='john@example.com', password='password')
        db.session.add(u)
        db.session.commit()

        # Delete the user
        u = User.query.filter_by(username='john').first()
        db.session.delete(u)
        db.session.commit()

        u = User.query.filter_by(username='john').first()
        self.assertIsNone(u)

# Run the tests with: python -m unittest test_user_model.py
#Replace 'john', 'john@example.com', and 'new_john@example.com' with appropriate test values. Note that the test_user_deletion test will remove the user, so it should be the last test run that involves the user with username 'john'.







if __name__ == '__main__':
    unittest.main(verbosity=2)
