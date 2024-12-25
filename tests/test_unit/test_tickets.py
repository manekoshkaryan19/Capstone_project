import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app import create_app
from routes.ticket import create_ticket, get_tickets, update_ticket, delete_ticket
from models.ticket import Ticket
from models.section import Section
from models.user import User


class TicketUnitTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        # Pop the context
        self.app_context.pop()

    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('flask_jwt_extended.utils.get_jwt', return_value={"sub": 999})
    @patch('flask_jwt_extended.utils.get_jwt_identity', return_value=999)
    @patch('models.section.Section.query')
    @patch('models.user.User.query')
    @patch('models.db.session.add')
    @patch('models.db.session.commit')
    def test_create_ticket(
        self,
        mock_commit,
        mock_add,
        mock_user_query,
        mock_section_query,
        mock_get_jwt_identity,
        mock_get_jwt,
        mock_verify_jwt
    ):

        # Mock a valid section
        mock_section = MagicMock(spec=Section)
        mock_section.id = 10
        mock_section_query.get.return_value = mock_section

        # Mock an assigned user if assigned_user_id is given
        mock_assigned_user = MagicMock(spec=User)
        mock_assigned_user.id = 123
        mock_user_query.get.return_value = mock_assigned_user

        with self.app.test_request_context('/create', method='POST'):
            with patch('flask.request.get_json') as mock_get_json:
                mock_get_json.return_value = {
                    'name': 'Test Ticket',
                    'description': 'Unit test description',
                    'section_id': 10,
                    'assigned_user_id': 123
                }
                response = create_ticket()  # returns (jsonify(...), 201)

        self.assertEqual(response[1], 201)
        data = response[0].json
        self.assertIn('id', data)
        self.assertEqual(data['name'], 'Test Ticket')
        self.assertEqual(data['description'], 'Unit test description')
        self.assertEqual(data['section_id'], 10)

        mock_add.assert_called_once()
        mock_commit.assert_called_once()


    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('flask_jwt_extended.utils.get_jwt', return_value={"sub": 777})
    @patch('flask_jwt_extended.utils.get_jwt_identity', return_value=777)
    @patch('models.section.Section.query')
    @patch('models.ticket.Ticket.query')
    def test_get_tickets(
        self,
        mock_ticket_query,
        mock_section_query,
        mock_get_jwt_identity,
        mock_get_jwt,
        mock_verify_jwt
    ):

        # Mock a valid section
        mock_section = MagicMock(spec=Section)
        mock_section.id = 5
        mock_section_query.get.return_value = mock_section

        # Mock 2 tickets
        mock_ticket1 = MagicMock(spec=Ticket)
        mock_ticket1.id = 101
        mock_ticket1.name = 'Ticket A'
        mock_ticket1.description = 'Desc A'
        mock_ticket1.assigned_user_id = None

        mock_ticket2 = MagicMock(spec=Ticket)
        mock_ticket2.id = 102
        mock_ticket2.name = 'Ticket B'
        mock_ticket2.description = 'Desc B'
        mock_ticket2.assigned_user_id = 42

        # Ticket.query.filter_by(section_id=5).all() => [mock_ticket1, mock_ticket2]
        mock_ticket_query.filter_by.return_value.all.return_value = [mock_ticket1, mock_ticket2]

        with self.app.test_request_context('/5', method='GET'):
            response = get_tickets(5)  # returns (jsonify([...]), 200)

        self.assertEqual(response[1], 200)
        data = response[0].json
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 101)
        self.assertEqual(data[1]['name'], 'Ticket B')


    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('flask_jwt_extended.utils.get_jwt', return_value={"sub": 777})
    @patch('flask_jwt_extended.utils.get_jwt_identity', return_value=777)
    @patch('models.ticket.Ticket.query')
    @patch('models.section.Section.query')
    @patch('models.user.User.query')
    @patch('models.db.session.commit')
    def test_update_ticket(
        self,
        mock_commit,
        mock_user_query,
        mock_section_query,
        mock_ticket_query,
        mock_get_jwt_identity,
        mock_get_jwt,
        mock_verify_jwt
    ):

        # Mock existing ticket
        mock_ticket = MagicMock(spec=Ticket)
        mock_ticket.id = 200
        mock_ticket.name = 'Old Ticket'
        mock_ticket.description = 'Old Desc'
        mock_ticket.section_id = 10

        # Give the ticket an old section with board_id=2
        mock_old_section = MagicMock(spec=Section)
        mock_old_section.board_id = 2
        mock_ticket.section = mock_old_section

        mock_ticket_query.get.return_value = mock_ticket

        # If assigned_user_id is updated
        mock_assigned_user = MagicMock(spec=User)
        mock_assigned_user.id = 456
        mock_user_query.get.return_value = mock_assigned_user

        # If new_section_id is present
        mock_section = MagicMock(spec=Section)
        mock_section.id = 11
        mock_section.board_id = 2  # Matches the old board ID
        mock_section_query.get.return_value = mock_section

        with self.app.test_request_context('/200', method='PUT'):
            with patch('flask.request.get_json') as mock_get_json:
                mock_get_json.return_value = {
                    'name': 'Updated Ticket',
                    'description': 'Updated Desc',
                    'assigned_user_id': 456,
                    'section_id': 11
                }
                response = update_ticket(200)  # (Response, 200)

        self.assertEqual(response[1], 200)  # Expecting 200
        data = response[0].json
        self.assertEqual(data['id'], 200)
        self.assertEqual(data['name'], 'Updated Ticket')
        self.assertEqual(data['description'], 'Updated Desc')
        self.assertEqual(data['section_id'], 11)

        # Confirm mock_ticket was updated
        self.assertEqual(mock_ticket.name, 'Updated Ticket')
        self.assertEqual(mock_ticket.description, 'Updated Desc')
        self.assertEqual(mock_ticket.section_id, 11)
        self.assertEqual(mock_ticket.assigned_user_id, 456)

        mock_commit.assert_called_once()


    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('flask_jwt_extended.utils.get_jwt', return_value={"sub": 777})
    @patch('flask_jwt_extended.utils.get_jwt_identity', return_value=777)
    @patch('models.ticket.Ticket.query')
    @patch('models.db.session.delete')
    @patch('models.db.session.commit')
    def test_delete_ticket(
        self,
        mock_commit,
        mock_delete,
        mock_ticket_query,
        mock_get_jwt_identity,
        mock_get_jwt,
        mock_verify_jwt
    ):

        # Mock an existing ticket
        mock_ticket = MagicMock(spec=Ticket)
        mock_ticket.id = 300
        mock_ticket_query.get.return_value = mock_ticket

        with self.app.test_request_context('/300', method='DELETE'):
            response = delete_ticket(300)  # (Response, 200)

        self.assertEqual(response[1], 200)
        data = response[0].json
        self.assertEqual(data['message'], 'Ticket deleted')

        mock_delete.assert_called_once_with(mock_ticket)
        mock_commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
