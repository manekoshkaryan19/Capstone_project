from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from routes import auth_bp, board_bp, section_bp, ticket_bp
from flask_migrate import Migrate


app = Flask(__name__, static_folder="static")
app.config.from_object(Config)


migrate = Migrate(app, db)
db.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(board_bp, url_prefix='/boards')
app.register_blueprint(section_bp, url_prefix='/sections')
app.register_blueprint(ticket_bp, url_prefix='/tickets')
# Health Check Endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200
# Welcome Endpoint
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the Capstone Application!"}), 200



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
