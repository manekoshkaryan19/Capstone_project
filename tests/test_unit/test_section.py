import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app import app
from routes.section import create_section, get_sections, update_section, delete_section
from models.section import Section
from models.board import Board
from models import db

class SectionUnitTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('flask_jwt_extended.utils.get_jwt', return_value={"sub": 123})
    @patch('flask_jwt_extended.utils.get_jwt_identity', return_value=123)
    @patch('models.board.Board.query')
    @patch('models.db.session.add')
    @patch('models.db.session.commit')
    def test_create_section(
        self,
        mock_commit,
        mock_add,
        mock_board_query,
        mock_get_jwt_identity,
        mock_get_jwt,
        mock_verify_jwt
    ):
        mock_board = MagicMock(spec=Board)
        mock_board.id = 10
        mock_board_query.filter.return_value.first.return_value = mock_board

        with self.app.test_request_context('/10/create', method='POST'):
            with patch('flask.request.get_json') as mock_get_json:
                mock_get_json.return_value = {
                    'name': 'New Section',
                    'description': 'Section for testing'
                }
                response = create_section(10)

        self.assertEqual(response[1], 201)
        data = response[0].json
        self.assertEqual(data['board_id'], 10)
        mock_add.assert_called_once()
        mock_commit.assert_called_once()

    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('flask_jwt_extended.utils.get_jwt', return_value={"sub": 123})
    @patch('flask_jwt_extended.utils.get_jwt_identity', return_value=123)
    @patch('models.board.Board.query')
    @patch('models.section.Section.query')
    def test_get_sections(
        self,
        mock_section_query,
        mock_board_query,
        mock_get_jwt_identity,
        mock_get_jwt,
        mock_verify_jwt
    ):
        mock_board = MagicMock(spec=Board)
        mock_board.id = 99
        mock_board_query.filter.return_value.first.return_value = mock_board

        mock_section1 = MagicMock(spec=Section)
        mock_section1.id = 1
        mock_section1.name = 'Section One'
        mock_section1.description = 'Desc One'

        mock_section2 = MagicMock(spec=Section)
        mock_section2.id = 2
        mock_section2.name = 'Section Two'
        mock_section2.description = 'Desc Two'

        mock_section_query.filter_by.return_value.all.return_value = [mock_section1, mock_section2]

        with self.app.test_request_context('/99', method='GET'):
            response = get_sections(99)

        self.assertEqual(response[1], 200)
        data = response[0].json
        self.assertEqual(len(data), 2)

    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('flask_jwt_extended.utils.get_jwt', return_value={"sub": 123})
    @patch('flask_jwt_extended.utils.get_jwt_identity', return_value=123)
    @patch('models.section.Section.query')
    @patch('models.board.Board.query')
    @patch('models.db.session.commit')
    def test_update_section(
        self,
        mock_commit,
        mock_board_query,
        mock_section_query,
        mock_get_jwt_identity,
        mock_get_jwt,
        mock_verify_jwt
    ):
        # Mock section object with a real integer board_id
        mock_section = MagicMock(spec=Section)
        mock_section.id = 7
        mock_section.name = 'Old Section'
        mock_section.description = 'Old Desc'
        mock_section.board_id = 50  # <-- Ensure board_id is an integer
        mock_section_query.join.return_value.filter.return_value.first.return_value = mock_section

        mock_board = MagicMock(spec=Board)
        mock_board.id = 50
        mock_board_query.filter.return_value.first.return_value = mock_board

        with self.app.test_request_context('/7', method='PUT'):
            with patch('flask.request.get_json') as mock_get_json:
                mock_get_json.return_value = {
                    'name': 'Updated Section',
                    'description': 'Updated Desc'
                }
                response = update_section(7)

        self.assertEqual(response[1], 200)
        data = response[0].json
        self.assertEqual(data['id'], 7)
        self.assertEqual(data['name'], 'Updated Section')
        self.assertEqual(data['description'], 'Updated Desc')
        self.assertEqual(data['board_id'], 50)

        self.assertEqual(mock_section.name, 'Updated Section')
        self.assertEqual(mock_section.description, 'Updated Desc')
        mock_commit.assert_called_once()

    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('flask_jwt_extended.utils.get_jwt', return_value={"sub": 123})
    @patch('flask_jwt_extended.utils.get_jwt_identity', return_value=123)
    @patch('models.section.Section.query')
    @patch('models.board.Board.query')
    @patch('models.db.session.delete')
    @patch('models.db.session.commit')
    def test_delete_section(
        self,
        mock_commit,
        mock_delete,
        mock_board_query,
        mock_section_query,
        mock_get_jwt_identity,
        mock_get_jwt,
        mock_verify_jwt
    ):
        mock_section = MagicMock(spec=Section)
        mock_section.id = 123
        mock_section_query.join.return_value.filter.return_value.first.return_value = mock_section

        mock_board = MagicMock(spec=Board)
        mock_board.id = 50
        mock_board_query.filter.return_value.first.return_value = mock_board

        with self.app.test_request_context('/123', method='DELETE'):
            response = delete_section(123)

        self.assertEqual(response[1], 200)
        data = response[0].json
        self.assertEqual(data['message'], 'Section deleted successfully')
        mock_delete.assert_called_once_with(mock_section)
        mock_commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
