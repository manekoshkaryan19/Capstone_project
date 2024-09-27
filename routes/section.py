from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Section, Board
from . import section_bp  

@section_bp.route('/<int:board_id>/create', methods=['POST'])
@jwt_required()
def create_section(board_id):
    user_id = get_jwt_identity()
    board = Board.query.filter(Board.id == board_id, (Board.users.any(id=user_id) | (Board.owner_id == user_id))).first()
    if not board:
        return jsonify({'message': 'Board not found or you do not have access to it.'}), 403

    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    if not name:
        return jsonify({'error': 'Section name is required'}), 400

    new_section = Section(name=name, description=description,  board_id=board_id)
    db.session.add(new_section)
    db.session.commit()

    return jsonify({
        "id": new_section.id,
        "name": new_section.name,
        "description": new_section.description,
        "board_id": new_section.board_id
    }), 201

@section_bp.route('/<int:board_id>', methods=['GET'])
@jwt_required()
def get_sections(board_id):
    user_id = get_jwt_identity()
    board = Board.query.filter(Board.id == board_id,(Board.users.any(id=user_id) | (Board.owner_id == user_id))).first()

    if not board:
        return jsonify({'message': 'Board not found or you do not have access to it.'}), 403

    sections = Section.query.filter_by(board_id=board_id).all()

    return jsonify([{
        "id": section.id,
        "name": section.name,
        "description": section.description
    } for section in sections]), 200

@section_bp.route('/<int:section_id>', methods=['PUT'])
@jwt_required()
def update_section(section_id):
    user_id = get_jwt_identity()
    section = Section.query.join(Board).filter(Section.id == section_id,(Board.users.any(id=user_id) | (Board.owner_id == user_id))).first()


    if not section:
        return jsonify({'message': 'Section not found or you do not have access to it.'}), 403

    data = request.get_json()
    section.name = data.get('name', section.name)
    section.description = data.get('description', section.description)

    db.session.commit()

    return jsonify({
        "id": section.id,
        "name": section.name,
        "description": section.description,
        "board_id": section.board_id  # Parent board cannot be changed
    }), 200


@section_bp.route('/<int:section_id>', methods=['DELETE'])
@jwt_required()
def delete_section(section_id):
    user_id = get_jwt_identity()
    section = Section.query.join(Board).filter(Section.id == section_id,(Board.users.any(id=user_id) | (Board.owner_id == user_id))).first()
    if not section:
        return jsonify({'message': 'Section not found or you do not have access to it.'}), 403

    db.session.delete(section)
    db.session.commit()

    return jsonify({'message': 'Section deleted successfully'}), 200
