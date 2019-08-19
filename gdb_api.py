from config import Config
from models import User, Share, SharePrice
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import json
import requests
from datetime import datetime


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

    def addshare(self, issuercode):
        """
        Adds share details of specified share to database to database.

        Args:
            issuercode (str): ASX issued code of share to add.
        Returns:
            bool: True if sucessful, false if share doesn't exist or is already present.

        """
        # Check that share isn't already added to database
        share = self.session.query(Share).filter(Share.issuercode == issuercode).first()
        if(share is not None):
            return False
        # Get share data from ASX
        # TODO: Move ASX API call elsewhere
        address = "https://www.asx.com.au/asx/1/company/%s?fields=primary_share" % issuercode
        asxdata = requests.get(address).json()
        # Check if share data was not retrieved successfully
        if('code' not in asxdata and asxdata['code'] != issuercode):
            return False
        # Create new share record
        share = Share(
            issuercode = asxdata['code'],
            companyname = asxdata['name_short'],
            industrygroupname = asxdata['industry_group_name'],
            currentprice = float(asxdata['primary_share']['open_price']),
            marketcapitalisation = int(asxdata['primary_share']['market_cap']),
            sharecount = int(asxdata['primary_share']['number_of_shares']),
            daychangepercent = float(asxdata['primary_share']['change_in_percent'].strip('%'))/100,
            daychangeprice = float(asxdata['primary_share']['change_price'])
        )
        # Add share to share table and commit changes
        self.session.add(share)
        self.session.commit()
        # Return success
        return True
    
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

        Returns:
            bool: True if update was successful, false if any major error occurs.
        
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
            # Get issuer code
            issuercode = code[0]
            # Call ASX API
            address = "https://www.asx.com.au/asx/1/company/%s?fields=primary_share" % issuercode
            asxdata = requests.get(address).json()
            # Check that the data was successfully retreived
            if('code' not in asxdata and asxdata['code'] == issuercode):
                # If unsuccessful, skip this share and try the next one
                # TODO: Rather than skip, maybe throw an exception or make it return
                #       false after doing everything else, as some shares may be
                #       removed from ASX later and may not work correctly.
                continue
            # Add data to dictionary
            share_data[issuercode] = {
                "curr_price": asxdata['primary_share']['open_price'],
                "curr_mc": asxdata['primary_share']['market_cap'],
                "curr_sc": asxdata['primary_share']['number_of_shares'],
                "dc_percent": asxdata['primary_share']['change_in_percent'],
                "dc_price": asxdata['primary_share']['change_price']
            }
        # Iterate over each share and update its values
        for issuercode in share_data:
            # Get share data
            curr_price = float(share_data[issuercode]["curr_price"])
            curr_mc = int(share_data[issuercode]["curr_mc"])
            curr_sc = int(share_data[issuercode]["curr_sc"])
            dc_percent = float(share_data[issuercode]["dc_percent"].strip('%'))/100
            dc_price = float(share_data[issuercode]["dc_price"])
            # Update share field
            share = self.session.query(Share).get(issuercode)
            share.price = curr_price
            share.marketcapitalisation = curr_mc
            share.sharecount = curr_sc
            share.daychangepercent = dc_percent
            share.daychangeprice = dc_price
            # Create and add new share price record
            shareprice = SharePrice(
                issuercode = issuercode,
                recordtime = datetime.utcnow(),
                price = curr_price
            )
            self.session.add(shareprice)
            # Commit the changes
            self.session.commit()
        # Return true as update was successful
        return True
