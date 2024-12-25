import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app import create_app
from routes.auth import register, login
from models.user import User


class UserUnitTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch('models.user.User.query')
    @patch('models.db.session.add')
    @patch('models.db.session.commit')
    def test_register_user_success(self, mock_commit, mock_add, mock_user_query):
        mock_user_query.filter_by.return_value.first.return_value = None

        with self.app.test_request_context('/auth/register', method='POST'):
            with patch('flask.request.get_json') as mock_get_json:
                mock_get_json.return_value = {
                    'email': 'new_user@example.com',
                    'password': 'secret_pass',
                    'first_name': 'John',
                    'last_name': 'Doe'
                }
                response = register()

        resp, status_code = response
        self.assertEqual(status_code, 200)
        data = resp.json
        self.assertEqual(data['email'], 'new_user@example.com')
        self.assertEqual(data['first_name'], 'John')
        self.assertEqual(data['last_name'], 'Doe')

        mock_add.assert_called_once()
        mock_commit.assert_called_once()


    @patch('models.user.User.query')
    @patch('models.db.session.add')
    @patch('models.db.session.commit')
    def test_register_user_already_exists(self, mock_commit, mock_add, mock_user_query):
        mock_existing_user = MagicMock(spec=User)
        mock_existing_user.email = 'existing@example.com'
        mock_user_query.filter_by.return_value.first.return_value = mock_existing_user

        with self.app.test_request_context('/auth/register', method='POST'):
            with patch('flask.request.get_json') as mock_get_json:
                mock_get_json.return_value = {
                    'email': 'existing@example.com',
                    'password': 'secret_pass',
                    'first_name': 'Jane',
                    'last_name': 'Smith'
                }
                response = register()

        resp, status_code = response
        self.assertEqual(status_code, 400)
        self.assertEqual(resp.json['message'], 'User already exists')

        mock_add.assert_not_called()
        mock_commit.assert_not_called()


    @patch('models.user.User.query')
    def test_login_success(self, mock_user_query):
        # Provide a REAL int for user.id to avoid "MagicMock not JSON serializable"
        mock_user = MagicMock(spec=User)
        mock_user.id = 123       # <-- Important fix
        mock_user.check_password.return_value = True
        mock_user_query.filter_by.return_value.first.return_value = mock_user

        with self.app.test_request_context('/auth/login', method='POST'):
            with patch('flask.request.get_json') as mock_get_json:
                mock_get_json.return_value = {
                    'email': 'valid@example.com',
                    'password': 'correct_pass'
                }
                response = login()

        resp, status_code = response
        self.assertEqual(status_code, 200)
        data = resp.json
        self.assertIn('access_token', data)
        self.assertTrue(len(data['access_token']) > 0)


    @patch('models.user.User.query')
    def test_login_invalid_credentials(self, mock_user_query):
        mock_user_query.filter_by.return_value.first.return_value = None

        with self.app.test_request_context('/auth/login', method='POST'):
            with patch('flask.request.get_json') as mock_get_json:
                mock_get_json.return_value = {
                    'email': 'wrong@example.com',
                    'password': 'wrong_pass'
                }
                response = login()

        resp, status_code = response
        self.assertEqual(status_code, 401)
        data = resp.json
        self.assertEqual(data['message'], 'Invalid credentials')


if __name__ == '__main__':
    unittest.main()
