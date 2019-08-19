from config import Config
from models import User, Share, SharePrice
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import json
import requests


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
            except VerifyMismatchError:
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

    def getshares(self):
        """
        Returns a list of all shares contained in the database.

        Returns:
            A list of every share in the database with stored data.

        """
        return self.session.query(Share).all()
    
    def updateshares(self):
        """
        Updates share and share price tables with new values from ASX.
        Calls ASX API in this method directly.
        
        Note: May be updated to be passed share data rather than do API calls here.
            Proposed data structure to be passed:
            <issuer code>:{
                curr_price: <Current price of share>
                curr_mc: <Current market cap of share>
                curr_sc: <Current total number of shares>
                dc_percent: <Current daily price change percent>
                dc_price: <Current daily price change>
            } 
        """
        # Get issuer codes for all currently stored shares
        share_codes = self.session.query(Share.issuercode).all()
        share_data = dict()
        # Iterate over each share issuer code
        for code in share_codes:
            # Call ASX API
            address = "https://www.asx.com.au/asx/1/company/%s?fields=primary_share" % code[0]
            asxdata = requests.get(address).json()
            # Add data to dictionary
            share_data[code] = {
                "curr_price": asxdata['primary_share']['open_price'],
                "curr_mc": asxdata['primary_share']['market_cap'],
                "curr_sc": asxdata['primary_share']['number_of_shares'],
                "dc_percent": asxdata['primary_share']['change_in_percent'],
                "dc_price": asxdata['primary_share']['change_price']
            }
        # Iterate over each share
        for issuer_id in share_data:
            # Get share data
            curr_price = share_data[issuer_id]["curr_price"]
            curr_mc = share_data[issuer_id]["curr_mc"]
            curr_sc = share_data[issuer_id]["curr_sc"]
            dc_percent = share_data[issuer_id]["curr_percent"]
            dc_price = share_data[issuer_id]["curr_price"]
            # Update share field
            share = self.session.query(Share).get(issuer_id)
            share.price = curr_price
            share.marketcapitalisation = curr_mc
            share.sharecount = curr_sc
            share.daychangepercent = dc_percent
            share.daychangeprice = dc_price
            # Create and add new share price record
            shareprice = SharePrice(
                issuercode = issuer_id,
                price = curr_price
            )
            self.session.add(shareprice)
            # Commit the changes
            self.session.commit()
