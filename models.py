from config import Config
from sqlalchemy import (Column, Integer, String, Boolean, BigInteger,
                        Float, Date, DateTime, ForeignKey, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
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
    dob = Column(Date, unique=False, nullable=False)
    gender = Column(String(20), unique=False, nullable=False)
    username = Column(String(64), index=True, unique=True)
    userpass = Column(String(200), unique=False, nullable=False)
    verified = Column(Boolean, unique=False, nullable=False)
    balance = Column(Float, unique=False, nullable=False)

    def get_id(self):
        return self.userID


class Usershare(Base):
    """ Model for Usershares """
    # TODO: Consider removing this table or adding more useful info
    # Table name
    __tablename__ = "USERSHARE"
    # Table Columns
    userID = Column(Integer, ForeignKey('USER.userID'),
                    primary_key=True)
    issuerID = Column(String(3), ForeignKey('SHARE.issuerID'),
                      primary_key=True)
    profit = Column(Float, nullable=False, unique=False)
    loss = Column(Float, nullable=False, unique=False)
    quantity = Column(BigInteger, nullable=False, unique=False)


class Transaction(Base):
    """Model for Transaction"""
    # Table name
    __tablename__ = "TRANSACTION"
    # Table Columns
    transID = Column(Integer, primary_key=True)
    issuerID = Column(String(45), ForeignKey('SHARE.issuerID'),
                      primary_key=False)
    userID = Column(Integer, ForeignKey('USER.userID'), primary_key=False)
    datetime = Column(DateTime, nullable=False, unique=False)
    transtype = Column(String(1), nullable=False, unique=False)
    feeval = Column(Float, nullable=False, unique=False)
    stocktransval = Column(Float, nullable=False, unique=False)
    totaltransval = Column(Float, nullable=False, unique=False)
    quantity = Column(BigInteger, nullable=False, unique=False)
    status = Column(String(20), nullable=False)


class Share(Base):
    """Model for shares."""
    # Table name
    __tablename__ = 'SHARE'
    # Table Columns
    issuerID = Column(String(3), primary_key=True)
    abbrevname = Column(String(50), nullable=False, unique=True)
    shortname = Column(String(50), nullable=False, unique=True)
    industrysector = Column(String(50), nullable=True, unique=False)
    currentprice = Column(Float, nullable=False, unique=False)
    marketcapitalisation = Column(BigInteger, nullable=False, unique=False)
    sharecount = Column(BigInteger, nullable=False, unique=False)
    daychangepercent = Column(Float, nullable=False, unique=False)
    daychangeprice = Column(Float, nullable=False, unique=False)


class SharePrice(Base):
    """Model for share price record."""
    # Table name
    __tablename__ = 'SHAREPRICE'
    # Table Columns
    issuerID = Column(String(3), ForeignKey('SHARE.issuerID'),
                      primary_key=True)
    recordtime = Column(DateTime, primary_key=True)
    price = Column(Float, nullable=False, unique=False)


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
