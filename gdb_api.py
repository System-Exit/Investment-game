from config import Config
from models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class GoogleDatabaseAPI:
    """
    API class for handling calls to google cloud SQL database

    """
    def __init__(self):
        """
        Initialise connection to database and setup API

        """
        # Define SQL connection parameters
        drivername = 'mysql+pymysql'
        username = Config.GDB_USERNAME
        password = Config.GDB_PASSWORD
        host = Config.GDB_HOST
        database = Config.GDB_DATABASE
        # Create engine
        engine = create_engine("%s://%s:%s@%s/%s" % (drivername, username, password, host, database))
        # Start session
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def adduser(self, username, password, firstname, lastname, email, gender):
        # Create user
        user = User(
            firstname=firstname, 
            lastname=lastname, 
            email=email,
            gender=gender, 
            username=username, 
            userpassword=password, 
            verfied= "Y"
            )
        # Add user to database
        self.session.add(user)
        self.session.commit()
        