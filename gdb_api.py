from config import Config
from models import User, Share, SharePrice, Usershare, Transaction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from contextlib import contextmanager
import json
import requests
from datetime import datetime, date


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
        # Define session maker
        self.Session = sessionmaker(bind=engine)

    @contextmanager
    def sessionmanager(self):
        """
        Context manager for handling sessions.
        Can often used

        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def adduser(self, username, userpass, firstname,
                lastname, email, dob, gender):
        """
        Add new user to user database table with given details.
        Also handles hashing and salting of given password.

        Args:
            username (str): Username for new user.
            userpass (str): Password for new user.
            firstname (str): First name of new user.
            lastname (str): Last name of new user.
            email (str): Email of new user.
            dob (date): Date of birth of new user.
            gender (str): Gender identity of new user.

        Returns:
            bool: Whether or not the user was added.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Check that username is available. If not, return false.
            user = session.query(User).filter(
                   User.username == username).first()
            if(user is not None):
                return False
            # Hash password
            passhash = PasswordHasher().hash(userpass)
            # Create user
            user = User(
                firstname=str(firstname),
                lastname=str(lastname),
                email=str(email),
                dob=dob,
                gender=str(gender),
                username=str(username),
                userpass=str(passhash),
                verified=True,
                balance=1000000
                )
            # Add user to database
            session.add(user)
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
            User ID if the user exists and password is valid, None otherwise.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Initialise password hasher
            ph = PasswordHasher()
            # Query if user exists
            user = session.query(User).filter(
                   User.username == username).first()
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
                # Since user exists and password is valid, return true
                return True, user.userID
            else:
                # User doesn't exist, return false
                return False, None

    def getuser(self, session, userID):
        """
        Gets and returns user object based on given ID.
        This needs to be given a session, as the returned model is
        connected to the session it is aquired from.

        Args:
            session: Session from context manager defined in this class.
            userID (str): The ID of the user to get.
        Returns:
            The user model object for that user.
        """
        # Get user
        user = session.query(User).get(userID)
        # Return user
        return user

    def addshare(self, issuercode):
        """
        Adds share details of specified share to database to database.

        Args:
            issuercode (str): ASX issued code of share to add.
        Returns:
            bool: True if sucessful, false if share doesn't exist or is
                  already present.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Check that share isn't already added to database
            share = session.query(Share).filter(
                Share.issuerID == issuercode).first()
            if(share is not None):
                return False
            # Get share data from ASX
            # TODO: Move ASX API call elsewhere
            address = ("https://www.asx.com.au/asx/1/company/"
                       f"{issuercode}?fields=primary_share")
            asxdata = requests.get(address).json()
            # Check if share data was not retrieved successfully
            if('code' not in asxdata and asxdata['code'] != issuercode):
                return False
            # Create new share record
            share = Share(
                issuerID=asxdata['code'],
                abbrevname=asxdata['name_abbrev'],
                shortname=asxdata['name_short'],
                industrysector=asxdata['sector_name'],
                currentprice=float(
                    asxdata['primary_share']['last_price']),
                marketcapitalisation=int(
                    asxdata['primary_share']['market_cap']),
                sharecount=int(
                    asxdata['primary_share']['number_of_shares']),
                daychangepercent=float(
                    asxdata['primary_share']['change_in_percent'].
                    strip('%'))/100,
                daychangeprice=float(
                    asxdata['primary_share']['change_price'])
            )
            # Add share to share table
            session.add(share)
            # Return success
            return True

    def getshares(self):
        """
        Returns a list of all shares contained in the database.

        Returns:
            A list of every share in the database with stored data.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Get shares
            shares = session.query(Share).all()
            # Initialise share list
            sharelist = list()
            # Iterate over shares and get share data
            for share in shares:
                # Append share data to share list
                sharelist.append(
                    {
                        "issuerID": share.issuerID,
                        "abbrevname": share.abbrevname,
                        "shortname": share.shortname,
                        "industrysector": share.industrysector,
                        "currentprice": share.currentprice,
                        "marketcapitalisation": share.marketcapitalisation,
                        "sharecount": share.sharecount,
                        "daychangepercent": share.daychangepercent,
                        "daychangeprice": share.daychangeprice
                    }
                )
            # Return share data
            return sharelist

    def updateshares(self):
        """
        Updates share and share price tables with new values from ASX.
        Calls ASX API in this method directly.

        Returns:
            bool: True if update was successful, false if any
                  major error occurs.

        Note: May be updated to be passed share data rather
              than do API calls here.
            Proposed data structure to be passed:
            <issuer code>:{
                curr_price: <Current price of share>
                curr_mc: <Current market cap of share>
                curr_sc: <Current total number of shares>
                dc_percent: <Current daily price change percent>
                dc_price: <Current daily price change>
            }
        """
        # Initialse session
        with self.sessionmanager() as session:
            # Get issuer codes for all currently stored shares
            share_codes = session.query(Share.issuerID).all()

        # Initialise share data
        share_data = dict()
        # Iterate over each share issuer code
        for code in share_codes:
            # Get issuer code
            issuerID = code[0]
            # Call ASX API
            address = ("https://www.asx.com.au/asx/1/share/"
                       "%s?fields=primary_share") % issuerID
            asxdata = requests.get(address).json()
            # Check that the data was successfully retreived
            if('code' not in asxdata and asxdata['code'] == issuerID):
                # If unsuccessful, skip this share and try the next one
                # TODO: Rather than skip, maybe throw an exception or make it
                #       return false after doing everything else, as some
                #       shares may be removed from ASX later and may not
                #       work correctly.
                continue
            # Add data to dictionary
            share_data[issuerID] = {
                "curr_price": asxdata['last_price'],
                "curr_mc": asxdata['market_cap'],
                "curr_sc": asxdata['number_of_shares'],
                "dc_percent": asxdata['change_in_percent'],
                "dc_price": asxdata['change_price']
            }

        # Initialse session
        with self.sessionmanager() as session:
            # Iterate over each share and update its values
            for issuerID in share_data:
                # Get share data
                curr_price = float(
                    share_data[issuerID]["curr_price"])
                curr_mc = int(
                    share_data[issuerID]["curr_mc"])
                curr_sc = int(
                    share_data[issuerID]["curr_sc"])
                dc_percent = float(
                    share_data[issuerID]["dc_percent"].strip('%'))/100
                dc_price = float(
                    share_data[issuerID]["dc_price"])
                # Update share field
                share = session.query(Share).get(issuerID)
                share.price = curr_price
                share.marketcapitalisation = curr_mc
                share.sharecount = curr_sc
                share.daychangepercent = dc_percent
                share.daychangeprice = dc_price
                # Create and add new share price record
                shareprice = SharePrice(
                    issuerID=issuerID,
                    recordtime=datetime.utcnow(),
                    price=curr_price
                )
                session.add(shareprice)
        # Return true as update was successful
        return True

    def buyshare(self, userID, issuerID, quantity):
        """
        Adds a new transaction of a user purchasing shares.
        Also updates user shares table.
        TODO: Return reason for false return

        Args:
            userID (str): ID of user that is making the purchase.
            issuerID (str): ID of share that is being purchased.
            quantity (int): Ammount of shares being purchased.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Check that user exists
            user = session.query(User).get(userID)
            if(user is None):
                return False
            # Check that share exists
            share = session.query(Share).get(issuerID)
            if(share is None):
                return False
            # Calculate costs for purchase including fee
            sharesprice = (share.currentprice * quantity)
            feesprice = 50 + (sharesprice * 0.01)
            totalprice = (sharesprice + feesprice)
            # Check that user can purchase share
            if(user.balance < totalprice):
                return False
            # Create and add transaction
            transaction = Transaction(
                issuerID=issuerID,
                userID=userID,
                datetime=datetime.utcnow(),
                transtype='B',
                feeval=feesprice,
                stocktransval=sharesprice,
                totaltransval=totalprice,
                quantity=quantity,
                status="Valid"
            )
            session.add(transaction)
            # Update user shares table
            usershare = session.query(Usershare).filter(
                Usershare.userID == userID,
                Usershare.issuerID == issuerID).first()
            # If the share doesn't already exist, create new record
            if(usershare is None):
                usershare = Usershare(
                    userID=userID,
                    issuerID=issuerID,
                    profit=0,
                    loss=totalprice,
                    quantity=quantity
                )
                session.add(usershare)
            # Otherwise, update existing usershare record
            else:
                usershare.loss = usershare.loss + sharesprice
                usershare.quantity = usershare.quantity + quantity
            # Return true for success
            return True

    def sellshare(self, userID, issuerID, quantity):
        """
        Adds a new transaction of a user selling shares.
        Also updates user shares table.
        TODO: Return reason for false return

        Args:
            userID (str): ID of user that is making the sale.
            issuerID (str): ID of share that is being sold.
            quantity (int): Ammount of shares being sold.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Check that user exists
            user = session.query(User).get(userID)
            if(user is None):
                return False
            # Check that share exists
            share = session.query(Share).get(issuerID)
            if(share is None):
                return False
            # Check that user has shares
            usershare = session.query(Usershare).filter(
                Usershare.userID == userID,
                Usershare.issuerID == issuerID).first()
            if(usershare is None):
                return False
            # Check that user can sell the quantity of shares
            if(usershare.quantity < quantity):
                return False
            # Calculate costs for sale including fee
            sharesprice = (share.currentprice * quantity)
            feesprice = 50 + (sharesprice * 0.0025)
            totalprice = (sharesprice - feesprice)
            # Create and add transaction
            transaction = Transaction(
                issuerID=issuerID,
                userID=userID,
                datetime=datetime.utcnow(),
                transtype='S',
                feeval=feesprice,
                stocktransval=sharesprice,
                totaltransval=totalprice,
                quantity=quantity,
                status="Valid"
            )
            session.add(transaction)
            # Update user shares table
            usershare.profit = usershare.profit + totalprice
            usershare.quantity = usershare.quantity - quantity
            # Return true for success
            return True

if __name__ == "__main__":
    # Initialize API
    gdb = GoogleDatabaseAPI()
    # Add some default stocks
    # stocks = ["AMC", "ANZ", "BHP", "BXB", "CBA", "CSL", "GMG", "IAG",
    #           "MQG", "NAB", "RIO", "S32", "SCG", "SUN", "TCL", "TLS",
    #           "WBC", "WES", "WOW", "WPL"]
    # for stock in stocks:
    #     gdb.addshare(stock)
    # Attempt a purchase
    print(gdb.sellshare(1, "ANZ", 10))
