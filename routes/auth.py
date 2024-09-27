from flask import request, jsonify
from models.user import User
from models import db
from flask_jwt_extended import create_access_token, jwt_required
from . import auth_bp

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user:
        return jsonify({'message': 'User already exists'}), 400
    
    new_user = User(email=data['email'], first_name=data['first_name'], last_name=data['last_name'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'email': new_user.email, 'first_name': new_user.first_name, 'last_name': new_user.last_name}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401
