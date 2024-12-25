# app.py

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from config import Config, TestConfig
from models import db
from routes import auth_bp, board_bp, section_bp, ticket_bp
from flask_migrate import Migrate
from flask_cors import CORS
from models import User, Board, Section, Ticket

def create_app(config_class=Config):

    app = Flask(__name__, static_folder="static")
    app.config.from_object(config_class)

    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(board_bp, url_prefix='/boards')
    app.register_blueprint(section_bp, url_prefix='/sections')
    app.register_blueprint(ticket_bp, url_prefix='/tickets')

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "healthy"}), 200

    @app.route('/', methods=['GET'])
    def index():
        return jsonify({"message": "Welcome to the Capstone Application!"}), 200

    CORS(app, resources={r"/*": {"origins": "*"}})
    return app

app = create_app()

if __name__ == '__main__':
    # Create app instance with default Config
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
