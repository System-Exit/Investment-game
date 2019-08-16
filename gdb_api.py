from config import Config
from models import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class GoogleDatabaseAPI:
    """
    API class for handling calls to google cloud SQL database.

    """
    def __init__(self):
        """
        Initialise connection to database and setup API.

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

    def adduser(self, username, userpass, firstname, lastname, email, gender):
        """
        Add new user to user database table with given details.
        Also handles hashing and salting of given password.

        Args:
            username (str): Username for new user.
            userpass (str): Password for new user.
            firstname (str): First name of new user.
            lastname (str): Last name of new user.
            email (str): Email of new user.
            gender (str): Gender identity of new user.
        
        Returns:
            bool: Whether or not the user was added.

        """
        # Check that username is available. If not, return false.
        user = self.session.query(User).filter(User.username == username).first()
        if(user is not None):
            return False
        
        # Hash password
        passhash = PasswordHasher().hash(userpass)
        # Create user
        user = User(
            firstname=firstname, 
            lastname=lastname, 
            email=email,
            gender=gender, 
            username=username, 
            userpass=passhash, 
            verified= True
            )
        # Add user to database
        self.session.add(user)
        self.session.commit()
        # Return success
        return True

    def verifyuser(self, username, userpass):
        """
        Verifies if the user with the given username and password exists.

        Args:
            username (str): Username of user to verify.
            userpass (str): Password of user to verify.

        Retruns:
            True if the user exists and the password is valid, otherwise false.
            User model object for user if valid, otherwise None.

        """
        # Initialise passwor hasher
        ph = PasswordHasher()
        # Query if user exists
        user = self.session.query(User).filter(User.username == username).first()
        # Check if query returns a user
        if(user is not None):
            # Verify whether the password is valid or not
            try:
                ph.verify(user.userpass, userpass)
            except VerifyMismatchError as e:
                # Password does not match, return false
                return False, None
            # Check if password needs to be rehashed
            if(ph.check_needs_rehash(user.userpass)):
                # Generate new hash
                rehash = ph.hash(userpass)
                # Update user record to include new hash
                user.userpass = rehash
                self.session.commit()
            # Since user exists and password is valid, return true
            return True, user
        else:
            # User doesn't exist, return false
            return False, None

    def getuser(self, userID):
        """
        Gets and returns user object based on given ID.
        Args:
            userID (str): The ID of the user to get.
        Returns:
            The user model object for that user.
        """
        return self.session.query(User).get(userID)

        