from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from routes import auth_bp, board_bp, section_bp, ticket_bp
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)


migrate = Migrate(app, db)
db.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(board_bp,  url_prefix='/boards')
app.register_blueprint(section_bp)
app.register_blueprint(ticket_bp)

with app.app_context():
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
