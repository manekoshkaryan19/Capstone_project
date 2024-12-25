# tests/test_integration/test_integration_board.py

import unittest
from app import create_app, db
from config import TestConfig
from models import User, Board  # Ensure all models are imported


class IntegrationBoardTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        # Create all tables
        db.create_all()

        # Create a test user
        self.user = User(email="owner@example.com", first_name="Owner", last_name="User")
        self.user.set_password("password123")
        db.session.add(self.user)
        db.session.commit()

        # Log in the test user
        login_response = self.client.post('/auth/login', json={
            'email': 'owner@example.com',
            'password': 'password123'
        })
        self.jwt = login_response.get_json().get('access_token')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_and_fetch_board(self):
        # Create a board
        board_response = self.client.post('/boards/create', json={
            'name': 'Integration Board',
            'description': 'Board for integration test'
        }, headers={'Authorization': f'Bearer {self.jwt}'})
        self.assertEqual(board_response.status_code, 201)
        board_id = board_response.get_json()['id']

        # Fetch board details
        details_response = self.client.get(f'/boards/{board_id}/details', headers={
            'Authorization': f'Bearer {self.jwt}'
        })
        self.assertEqual(details_response.status_code, 200)
        details = details_response.get_json()
        self.assertEqual(details['name'], 'Integration Board')

    def test_invite_and_access_board(self):
        # Create a board
        board_response = self.client.post('/boards/create', json={
            'name': 'Invite Test Board',
            'description': 'Testing invitations'
        }, headers={'Authorization': f'Bearer {self.jwt}'})
        board_id = board_response.get_json()['id']
        invitation_token = board_response.get_json().get('invitation_token')

        # Create another user
        invitee = User(email="invitee@example.com", first_name="Invitee", last_name="User")
        invitee.set_password("password123")
        db.session.add(invitee)
        db.session.commit()

        # Authenticate the invitee
        login_response = self.client.post('/auth/login', json={
            'email': 'invitee@example.com',
            'password': 'password123'
        })
        invitee_jwt = login_response.get_json().get('access_token')

        # Join the board
        join_response = self.client.post(f'/boards/{invitation_token}/join', headers={
            'Authorization': f'Bearer {invitee_jwt}'
        })
        self.assertEqual(join_response.status_code, 200)
        self.assertIn('successfully joined', join_response.get_json().get('message', ''))


if __name__ == "__main__":
    unittest.main()
