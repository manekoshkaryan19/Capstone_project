from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.ticket import Ticket
from models.section import Section
from models.user import User
from . import ticket_bp

@ticket_bp.route('/create', methods=['POST'])
@jwt_required()
def create_ticket():
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    section_id = data.get('section_id')
    assigned_user_id = data.get('assigned_user_id')

    if not name or not section_id:
        return jsonify({"error": "Ticket name and section_id are required"}), 400

    section = Section.query.get(section_id)
    if not section:
        return jsonify({"error": "Section not found"}), 404
    
    if assigned_user_id:
        user = User.query.get(assigned_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

    new_ticket = Ticket(
        name=name,
        description=description,
        section_id=section_id,
        assigned_user_id = assigned_user_id,
        owner_id=user_id  
    )

    db.session.add(new_ticket)
    db.session.commit()

    return jsonify({
        "id": new_ticket.id,
        "name": new_ticket.name,
        "description": new_ticket.description,
        "section_id": new_ticket.section_id
    }), 201

@ticket_bp.route('/<int:section_id>', methods=['GET'])
@jwt_required()
def get_tickets(section_id):
    section = Section.query.get(section_id)
    if not section:
        return jsonify({"error": "Section not found"}), 404

    tickets = Ticket.query.filter_by(section_id=section_id).all()
    return jsonify([{
        "id": ticket.id,
        "name": ticket.name,
        "description": ticket.description,
        "assigned_user_id": ticket.assigned_user_id
    } for ticket in tickets]), 200


@ticket_bp.route('/<int:ticket_id>', methods=['PUT'])
@jwt_required()
def update_ticket(ticket_id):
    data = request.get_json()
    ticket = Ticket.query.get(ticket_id)

    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    new_section_id = data.get('section_id')
    name = data.get('name', ticket.name)  
    description = data.get('description', ticket.description)  
    assigned_user_id = data.get('assigned_user_id', ticket.assigned_user_id)

    if assigned_user_id:
        user = User.query.get(assigned_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
    if new_section_id and new_section_id != ticket.section_id:
        new_section = Section.query.get(new_section_id)
        if not new_section or new_section.board_id != ticket.section.board_id:
            return jsonify({"error": "New section must be on the same board"}), 400

        ticket.section_id = new_section_id

    ticket.name = name
    ticket.description = description
    ticket.assigned_user_id = assigned_user_id


    db.session.commit()

    return jsonify({
        "id": ticket.id,
        "name": ticket.name,
        "description": ticket.description,
        "section_id": ticket.section_id,
        
        
    }), 200

@ticket_bp.route('/<int:ticket_id>', methods=['DELETE'])
@jwt_required()
def delete_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)

    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    db.session.delete(ticket)
    db.session.commit()

    return jsonify({"message": "Ticket deleted"}), 200
