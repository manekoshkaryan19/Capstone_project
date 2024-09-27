from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
board_bp = Blueprint('board', __name__, url_prefix='/boards')
section_bp = Blueprint('section', __name__, url_prefix='/sections')
ticket_bp = Blueprint('ticket', __name__, url_prefix='/tickets')

from . import auth, board, section, ticket
