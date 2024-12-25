import unittest
from app import create_app, db
from config import TestConfig
from models import User, Board, Section  # Import all relevant models


class IntegrationSectionTestCase(unittest.TestCase):
    def setUp(self):

        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        self.user = User(
            email="owner@example.com",
            first_name="Owner",
            last_name="User"
        )
        self.user.set_password("password123")
        db.session.add(self.user)
        db.session.commit()
        login_response = self.client.post('/auth/login', json={
            'email': 'owner@example.com',
            'password': 'password123'
        })
        self.assertEqual(login_response.status_code, 200, "Login should succeed for valid credentials")
        self.jwt = login_response.get_json().get('access_token')
        self.assertIsNotNone(self.jwt, "JWT token should not be None")
        self.board = Board(
            name='Test Board',
            description='Board for sections',
            owner_id=self.user.id
        )
        db.session.add(self.board)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_and_fetch_sections(self):
        # Create three sections
        for i in range(3):
            response = self.client.post(
                f'/sections/{self.board.id}/create',
                json={
                    'name': f'Section {i + 1}',
                    'description': f'Description {i + 1}'
                },
                headers={'Authorization': f'Bearer {self.jwt}'}
            )
            self.assertEqual(response.status_code, 201, f"Section {i + 1} creation should return 201")
            self.assertEqual(
                response.get_json()['name'],
                f'Section {i + 1}',
                f"Section {i + 1} name should match"
            )

        # Fetch all sections for the board
        sections_response = self.client.get(
            f'/sections/{self.board.id}',
            headers={'Authorization': f'Bearer {self.jwt}'}
        )
        self.assertEqual(sections_response.status_code, 200, "Fetching sections should return 200")
        sections = sections_response.get_json()
        self.assertEqual(len(sections), 3, "There should be exactly 3 sections")

        expected_names = [f'Section {i + 1}' for i in range(3)]
        actual_names = [section['name'] for section in sections]
        self.assertListEqual(actual_names, expected_names, "Section names should match the created sections")


if __name__ == "__main__":
    unittest.main()
