
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.board import Board
from models import db, Section, Ticket, User
from sqlalchemy.orm import joinedload
from . import board_bp
from flask_mail import Message
import uuid


@board_bp.route('/', methods=['GET'])
@jwt_required()
def get_boards():
    user_id = get_jwt_identity()
    boards = Board.query.filter_by(owner_id=user_id).all()
    return jsonify([{'id': b.id, 'name': b.name, 'description': b.description} for b in boards])

@board_bp.route('/create', methods=['POST'])
@jwt_required()
def create_board():
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    if not name:
        return jsonify({"error": "Board name is required"}), 400

    invitation_token = str(uuid.uuid4())
    new_board = Board(name=name, description=description, owner_id=user_id, invitation_token=invitation_token)

    db.session.add(new_board)
    db.session.commit()

    return jsonify({
        "id": new_board.id,
        "name": new_board.name,
        "description": new_board.description,
        "owner_id": new_board.owner_id,
        "invitation_token": new_board.invitation_token,
    }), 201



@board_bp.route('/myboards', methods=['GET'])
@jwt_required() 
def get_user_boards():
    user_id = get_jwt_identity() 
    boards = Board.query.filter_by(owner_id=user_id).all()
    if not boards:
        return jsonify({"msg": "No boards found for this user"}), 404
    board_list = [{
        'id': board.id,
        'name': board.name,
        'description': board.description
    } for board in boards]
    return jsonify({'boards': board_list}), 200


@board_bp.route('/<int:board_id>/details', methods=['GET'])
@jwt_required()
def get_board_details(board_id):
    user_id = get_jwt_identity()
    board = Board.query.options(
        joinedload(Board.sections),
        joinedload(Board.users)
    ).filter(
        (Board.id == board_id) &
        ((Board.owner_id == user_id) | (Board.users.any(id=user_id)))
    ).first()

    if not board:
        return jsonify({'error': 'Board not found or not accessible'}), 404

    sections = [{
        'id': section.id,
        'name': section.name,
        'description': section.description,
        'tickets': [{'id': ticket.id, 'name': ticket.name, 'description': ticket.description} for ticket in section.tickets]
    } for section in board.sections]

    users = [{
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name
    } for user in board.users]

    return jsonify({
        'id': board.id,
        'name': board.name,
        'description': board.description,
        'owner_id': board.owner_id,
        'invitation_token': board.invitation_token,
        'sections': sections,
        'users': users
    }), 200

@board_bp.route('/<int:board_id>/invite', methods=['POST'])
@jwt_required()
def invite_user(board_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    invitee_email = data.get('email')
    board = Board.query.filter_by(id=board_id, owner_id=user_id).first()
    if not board:
        return jsonify({"error": "Board not found or you're not the owner"}), 404

    invitation_link = f"http://127.0.0.1:5000/boards/{board.invitation_token}/join"

    return jsonify({
        "invitation_link": invitation_link,
        "invitation_token": board.invitation_token
    }), 200

@board_bp.route('/<string:invitation_token>/join', methods=['POST'])
@jwt_required()
def join_board(invitation_token):
    user_id = get_jwt_identity()
    board = Board.query.filter_by(invitation_token=invitation_token).first()
    if not board:
        return jsonify({'error': 'Invalid or expired invitation token'}), 404

    user = User.query.get(user_id)
    if user not in board.users:
        board.users.append(user)
        db.session.commit()

    return jsonify({
        'message': f'{user.first_name} {user.last_name} has successfully joined the board {board.name}'
    }), 200


