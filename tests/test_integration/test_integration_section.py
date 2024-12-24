import unittest
from app import app, db
from models import User, Board, Section

class IntegrationSectionTestCase(unittest.TestCase):
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

        self.board = Board(name='Test Board', description='Board for sections', owner_id=self.user.id)
        db.session.add(self.board)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_and_fetch_sections(self):
        for i in range(3):
            response = self.app.post(f'/sections/{self.board.id}/create', json={
                'name': f'Section {i+1}',
                'description': f'Description {i+1}'
            }, headers={'Authorization': f'Bearer {self.jwt}'})
            self.assertEqual(response.status_code, 201)

        sections_response = self.app.get(f'/sections/{self.board.id}', headers={
            'Authorization': f'Bearer {self.jwt}'
        })
        self.assertEqual(sections_response.status_code, 200)
        sections = sections_response.get_json()
        self.assertEqual(len(sections), 3)

if __name__ == "__main__":
    unittest.main()
