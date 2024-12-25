import unittest
from app import create_app, db
from config import TestConfig
from models import User, Board, Section, Ticket  # Import all relevant models


class IntegrationTicketTestCase(unittest.TestCase):
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
            description='Board for tickets',
            owner_id=self.user.id
        )
        db.session.add(self.board)
        db.session.commit()
        self.section = Section(
            name='Test Section',
            description='Section for tickets',
            board_id=self.board.id
        )
        db.session.add(self.section)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_update_delete_ticket(self):
        response = self.client.post(
            '/tickets/create',
            json={
                'name': 'Test Ticket',
                'description': 'Ticket for testing',
                'section_id': self.section.id
            },
            headers={'Authorization': f'Bearer {self.jwt}'}
        )
        self.assertEqual(response.status_code, 201, "Ticket creation should return 201")
        ticket_id = response.get_json().get('id')
        self.assertIsNotNone(ticket_id, "Ticket ID should not be None")
        update_response = self.client.put(
            f'/tickets/{ticket_id}',
            json={
                'name': 'Updated Ticket',
                'description': 'Updated description'
            },
            headers={'Authorization': f'Bearer {self.jwt}'}
        )
        self.assertEqual(update_response.status_code, 200, "Ticket update should return 200")
        updated_ticket = update_response.get_json()
        self.assertEqual(updated_ticket['name'], 'Updated Ticket', "Ticket name should be updated")
        self.assertEqual(updated_ticket['description'], 'Updated description', "Ticket description should be updated")

        delete_response = self.client.delete(
            f'/tickets/{ticket_id}',
            headers={'Authorization': f'Bearer {self.jwt}'}
        )
        self.assertEqual(delete_response.status_code, 200, "Ticket deletion should return 200")
        self.assertEqual(delete_response.get_json().get('message'), 'Ticket deleted', "Deletion message should match")

    def test_reassign_ticket_to_new_section(self):
        new_section = Section(
            name='New Section',
            description='For reassignment',
            board_id=self.board.id
        )
        db.session.add(new_section)
        db.session.commit()

        response = self.client.post(
            '/tickets/create',
            json={
                'name': 'Ticket to Reassign',
                'description': 'Test ticket reassignment',
                'section_id': self.section.id
            },
            headers={'Authorization': f'Bearer {self.jwt}'}
        )
        self.assertEqual(response.status_code, 201, "Ticket creation should return 201")
        ticket_id = response.get_json().get('id')
        self.assertIsNotNone(ticket_id, "Ticket ID should not be None")
        reassign_response = self.client.put(
            f'/tickets/{ticket_id}',
            json={
                'section_id': new_section.id
            },
            headers={'Authorization': f'Bearer {self.jwt}'}
        )
        self.assertEqual(reassign_response.status_code, 200, "Ticket reassignment should return 200")
        reassigned_ticket = reassign_response.get_json()
        self.assertEqual(reassigned_ticket['section_id'], new_section.id,
                         "Ticket should be reassigned to the new section")


if __name__ == "__main__":
    unittest.main()
