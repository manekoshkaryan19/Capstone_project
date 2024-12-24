from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
test_db = SQLAlchemy()
from .section import Section
from .ticket import Ticket
from .user import User
from .board import Board