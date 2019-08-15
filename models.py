from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from flask_login import UserMixin

Base = declarative_base()

class User(Base, UserMixin):
    """Model for user accounts."""

    __tablename__ = 'USER'

    userID = Column(Integer, primary_key=True)
    firstname = Column(String(255), nullable=False, unique=False)
    lastname = Column(String(255), nullable=False, unique=False)
    email = Column(String(40), unique=True, nullable=False)
    gender = Column(String(20), unique=False, nullable=False)
    username = Column(String(64), index=True, unique=True)
    password = Column(String(200), unique=False, nullable=False)
    verified = Column(String(20), unique=False)
    