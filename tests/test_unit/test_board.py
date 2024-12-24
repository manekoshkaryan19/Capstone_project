import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app import app
from routes.board import create_board, get_boards, get_board_details
from models.board import Board
from models import db


class BoardUnitTestCase(unittest.TestCase):


    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    #
    # 1) Test CREATE BOARD
    #
    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('flask_jwt_extended.utils.get_jwt', return_value={"sub": 123})
    @patch('flask_jwt_extended.utils.get_jwt_identity', return_value=123)
    @patch('models.db.session.add')
    @patch('models.db.session.commit')
    def test_create_board(
        self,
        mock_commit,
        mock_add,
        mock_get_jwt_identity,
        mock_get_jwt,
        mock_verify_jwt
    ):
        """
        Tests POST /boards/create -> create_board().
        We expect 201 if 'name' is provided, along with new board data in JSON.
        """
        with self.app.test_request_context('/boards/create', method='POST'):
            with patch('flask.request.get_json') as mock_get_json:
                mock_get_json.return_value = {
                    'name': 'My Test Board',
                    'description': 'A board for testing'
                }
                response = create_board()  # returns (jsonify(...), status_code)

        resp, status_code = response
        self.assertEqual(status_code, 201)
        data = resp.json
        self.assertIn('id', data)
        self.assertEqual(data['name'], 'My Test Board')
        self.assertEqual(data['description'], 'A board for testing')
        self.assertEqual(data['owner_id'], 123)  # from mock_get_jwt_identity

        mock_add.assert_called_once()
        mock_commit.assert_called_once()

    #
    # 2) Test GET BOARDS
    #
    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('flask_jwt_extended.utils.get_jwt', return_value={"sub": 123})
    @patch('flask_jwt_extended.utils.get_jwt_identity', return_value=123)
    @patch('models.board.Board.query')
    def test_get_boards(
        self,
        mock_board_query,
        mock_get_jwt_identity,
        mock_get_jwt,
        mock_verify_jwt
    ):
        """
        Tests GET /boards -> get_boards().
        Should return 200 + a list of boards owned by user_id=123.
        """
        # Mock two boards
        mock_board1 = MagicMock(spec=Board)
        mock_board1.id = 10
        mock_board1.name = 'Board 10'
        mock_board1.description = 'Desc 10'

        mock_board2 = MagicMock(spec=Board)
        mock_board2.id = 11
        mock_board2.name = 'Board 11'
        mock_board2.description = 'Desc 11'

        mock_board_query.filter_by.return_value.all.return_value = [mock_board1, mock_board2]

        with self.app.test_request_context('/boards', method='GET'):
            response = get_boards()  # returns (jsonify(...), status_code)

        resp, status_code = response
        self.assertEqual(status_code, 200)
        data = resp.json
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 10)
        self.assertEqual(data[1]['name'], 'Board 11')

    #
    # 3) Test GET BOARD DETAILS
    #
    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('flask_jwt_extended.utils.get_jwt', return_value={"sub": 123})
    @patch('flask_jwt_extended.utils.get_jwt_identity', return_value=123)
    @patch('models.board.Board.query')
    def test_get_board_details(
        self,
        mock_board_query,
        mock_get_jwt_identity,
        mock_get_jwt,
        mock_verify_jwt
    ):
        """
        Tests GET /boards/<board_id>/details -> get_board_details(board_id).
        Expect 200 + correct board data if found.
        """
        mock_board = MagicMock(spec=Board)
        mock_board.id = 5
        mock_board.name = 'Board 5'
        mock_board.description = 'Desc 5'
        mock_board.owner_id = 123
        mock_board.invitation_token = 'abcdef'

        mock_board_query.options.return_value.filter.return_value.first.return_value = mock_board

        with self.app.test_request_context('/boards/5/details', method='GET'):
            response = get_board_details(5)

        resp, status_code = response
        self.assertEqual(status_code, 200)
        data = resp.json
        self.assertEqual(data['id'], 5)
        self.assertEqual(data['name'], 'Board 5')
        self.assertEqual(data['owner_id'], 123)
        self.assertEqual(data['invitation_token'], 'abcdef')


if __name__ == '__main__':
    unittest.main()
