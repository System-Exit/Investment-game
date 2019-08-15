from config import Config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from flask_login import UserMixin

Base = declarative_base()

class User(Base, UserMixin):
    """Model for user accounts."""
    # Table name
    __tablename__ = 'USER'
    # Table Columns
    userID = Column(Integer, primary_key=True)
    firstname = Column(String(255), nullable=False, unique=False)
    lastname = Column(String(255), nullable=False, unique=False)
    email = Column(String(40), unique=True, nullable=False)
    gender = Column(String(20), unique=False, nullable=False)
    username = Column(String(64), index=True, unique=True)
    userpass = Column(String(200), unique=False, nullable=False)
    verified = Column(Boolean, unique=False)

# Allow creation of tables by running API directly
if __name__ == "__main__":
    # Define SQL connection parameters
    drivername = 'mysql+pymysql'
    username = Config.GDB_USERNAME
    password = Config.GDB_PASSWORD
    host = Config.GDB_HOST
    database = Config.GDB_DATABASE
    query = Config.GDB_QUERY
    # Create engine
    engine = create_engine("%s://%s:%s@%s/%s%s" % (
        drivername, username, password, host, database, query))
    # Create tables
    Base.metadata.create_all(engine)