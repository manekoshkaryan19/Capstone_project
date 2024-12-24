import unittest
from app import app, db
from models import User, Board, Section, Ticket

class IntegrationTicketTestCase(unittest.TestCase):
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

        # Create a board and section for testing
        self.board = Board(name='Test Board', description='Board for tickets', owner_id=self.user.id)
        db.session.add(self.board)
        db.session.commit()

        self.section = Section(name='Test Section', description='Section for tickets', board_id=self.board.id)
        db.session.add(self.section)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_update_delete_ticket(self):
        response = self.app.post('/tickets/create', json={
            'name': 'Test Ticket',
            'description': 'Ticket for testing',
            'section_id': self.section.id
        }, headers={'Authorization': f'Bearer {self.jwt}'}
        )
        self.assertEqual(response.status_code, 201)
        ticket_id = response.get_json()['id']

        update_response = self.app.put(f'/tickets/{ticket_id}', json={
            'name': 'Updated Ticket',
            'description': 'Updated description'
        }, headers={'Authorization': f'Bearer {self.jwt}'}
        )
        self.assertEqual(update_response.status_code, 200)
        updated_ticket = update_response.get_json()
        self.assertEqual(updated_ticket['name'], 'Updated Ticket')
        self.assertEqual(updated_ticket['description'], 'Updated description')

        # Delete the ticket
        delete_response = self.app.delete(f'/tickets/{ticket_id}', headers={
            'Authorization': f'Bearer {self.jwt}'
        })
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.get_json()['message'], 'Ticket deleted')

    def test_reassign_ticket_to_new_section(self):

        new_section = Section(name='New Section', description='For reassignment', board_id=self.board.id)
        db.session.add(new_section)
        db.session.commit()

        response = self.app.post('/tickets/create', json={
            'name': 'Ticket to Reassign',
            'description': 'Test ticket reassignment',
            'section_id': self.section.id
        }, headers={'Authorization': f'Bearer {self.jwt}'}
        )
        self.assertEqual(response.status_code, 201)
        ticket_id = response.get_json()['id']

        # Reassign the ticket to the new section
        reassign_response = self.app.put(f'/tickets/{ticket_id}', json={
            'section_id': new_section.id
        }, headers={'Authorization': f'Bearer {self.jwt}'}
        )
        self.assertEqual(reassign_response.status_code, 200)
        reassigned_ticket = reassign_response.get_json()
        self.assertEqual(reassigned_ticket['section_id'], new_section.id)


if __name__ == "__main__":
    unittest.main()
