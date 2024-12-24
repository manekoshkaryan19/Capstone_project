import unittest
from app import app, db
from models import User, Board


class IntegrationBoardTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        self.user = User(email="owner@example.com", first_name="Owner", last_name="User")
        self.user.set_password("password123")
        db.session.add(self.user)
        db.session.commit()

        login_response = self.app.post('/auth/login', json={
            'email': 'owner@example.com',
            'password': 'password123'
        })
        self.jwt = login_response.get_json()['access_token']

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_and_fetch_board(self):
        # Create a board
        board_response = self.app.post('/boards/create', json={
            'name': 'Integration Board',
            'description': 'Board for integration test'
        }, headers={'Authorization': f'Bearer {self.jwt}'})
        self.assertEqual(board_response.status_code, 201)
        board_id = board_response.get_json()['id']

        # Fetch board details
        details_response = self.app.get(f'/boards/{board_id}/details', headers={
            'Authorization': f'Bearer {self.jwt}'
        })
        self.assertEqual(details_response.status_code, 200)
        details = details_response.get_json()
        self.assertEqual(details['name'], 'Integration Board')

    def test_invite_and_access_board(self):
        # Create a board
        board_response = self.app.post('/boards/create', json={
            'name': 'Invite Test Board',
            'description': 'Testing invitations'
        }, headers={'Authorization': f'Bearer {self.jwt}'})
        board_id = board_response.get_json()['id']
        invitation_token = board_response.get_json()['invitation_token']

        # Create another user
        invitee = User(email="invitee@example.com", first_name="Invitee", last_name="User")
        invitee.set_password("password123")
        db.session.add(invitee)
        db.session.commit()

        # Authenticate the invitee
        login_response = self.app.post('/auth/login', json={
            'email': 'invitee@example.com',
            'password': 'password123'
        })
        invitee_jwt = login_response.get_json()['access_token']

        # Join the board
        join_response = self.app.post(f'/boards/{invitation_token}/join', headers={
            'Authorization': f'Bearer {invitee_jwt}'
        })
        self.assertEqual(join_response.status_code, 200)
        self.assertIn('successfully joined', join_response.get_json()['message'])

if __name__ == "__main__":
    unittest.main()
