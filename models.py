
from flask_login import UserMixin

class User(UserMixin, db.Model):
    """Model for user accounts."""

    __tablename__ = 'USER'

    userID = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(255), nullable=False, unique=False)
    lastname = db.Column(db.String(255), nullable=False, unique=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    gender = db.Column(db.String(20), unique=False, nullable=False)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(200),, unique=False, nullable=False)
    verified = db.Column(db.String(20), unique=False)
    