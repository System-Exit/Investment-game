from config import Config
from models import User
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
        query = Config.GDB_QUERY
        # Create engine
        engine = create_engine("%s://%s:%s@%s/%s%s" % (
            drivername, username, password, host, database, query))
        # Start session
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def adduser(self, username, password, firstname, lastname, email, gender):
        """
        Add new user to user database table with given details

        Args:
            username (str): Username for new user
            password (str): Password for new user
            firstname (str): First name of new user
            lastname (str): Last name of new user
            email (str): Email of new user
            gender (str): Gender identity of new user

        """
        # Create user
        user = User(
            firstname=firstname, 
            lastname=lastname, 
            email=email,
            gender=gender, 
            username=username, 
            userpass=password, 
            verified= True
            )
        # Add user to database
        self.session.add(user)
        self.session.commit()

    def verifyuser(self, username, userpass):
        """
        TODO

        """
        pass

        