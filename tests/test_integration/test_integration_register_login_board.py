import unittest
from app import create_app, db
from config import TestConfig


class IntegrationAuthTestCase(unittest.TestCase):
    def setUp(self):
        # Create the app with TestConfig
        self.app = create_app(TestConfig)

        # Push the application context
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Initialize the test client
        self.client = self.app.test_client()

        # Create all tables
        db.create_all()

    def tearDown(self):
        # Remove session and drop all tables
        db.session.remove()
        db.drop_all()

        # Pop the application context
        self.app_context.pop()

    def test_register_login_and_create_board(self):
        # Register a new user
        register_response = self.client.post('/auth/register', json={
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123'
        })
        self.assertEqual(register_response.status_code, 200)

        # Login with the registered user
        login_response = self.client.post('/auth/login', json={
            'email': 'newuser@example.com',
            'password': 'password123'
        })
        self.assertEqual(login_response.status_code, 200)
        jwt_token = login_response.get_json().get('access_token')
        self.assertIsNotNone(jwt_token, "JWT token should not be None")

        # Create a board
        board_response = self.client.post('/boards/create', json={
            'name': 'New User Board',
            'description': 'Board created after login'
        }, headers={'Authorization': f'Bearer {jwt_token}'})
        self.assertEqual(board_response.status_code, 201)
        self.assertEqual(board_response.get_json()['name'], 'New User Board')

    def test_invalid_login(self):
        # Attempt login with invalid credentials
        login_response = self.client.post('/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(login_response.status_code, 401)
        self.assertIn('Invalid credentials', login_response.get_json().get('message', ''))


if __name__ == "__main__":
    unittest.main()
