import unittest
from app import app, db
from models import User

class IntegrationAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_login_and_create_board(self):
        # Register a new user
        register_response = self.app.post('/auth/register', json={
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123'
        })
        self.assertEqual(register_response.status_code, 200)

        # Login with the registered user
        login_response = self.app.post('/auth/login', json={
            'email': 'newuser@example.com',
            'password': 'password123'
        })
        self.assertEqual(login_response.status_code, 200)
        jwt_token = login_response.get_json()['access_token']

        # Create a board
        board_response = self.app.post('/boards/create', json={
            'name': 'New User Board',
            'description': 'Board created after login'
        }, headers={'Authorization': f'Bearer {jwt_token}'}
        )
        self.assertEqual(board_response.status_code, 201)
        self.assertEqual(board_response.get_json()['name'], 'New User Board')

    def test_invalid_login(self):
        # Attempt login with invalid credentials
        login_response = self.app.post('/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(login_response.status_code, 401)
        self.assertIn('Invalid credentials', login_response.get_json()['message'])


if __name__ == "__main__":
    unittest.main()
