from . import db

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False)
    board = db.relationship('Board', backref='sections')
