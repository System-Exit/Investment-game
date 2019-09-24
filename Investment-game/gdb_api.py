from models import User, Share, SharePrice, Usershare, Transaction, Admin
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from contextlib import contextmanager
import json
import requests
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import math


class GoogleDatabaseAPI:
    """
    API class for handling calls to google cloud SQL database.

    """
    def __init__(self, app=None):
        """
        Initialise API class.
        If given a flask app, will initialise API for app.

        """
        # If an app is passed, initialise with the app and return
        if app:
            self.init_app(app)
            return
        # Return without doing anything
        return

    def init_app(self, app):
        """
        Initialises database API for a flask app.

        Args:
            app: The Flask app to initialise database API for.

        """
        # Define SQL connection parameters
        drivername = 'mysql+pymysql'
        username = app.config['GDB_USERNAME']
        password = app.config['GDB_PASSWORD']
        host = app.config['GDB_HOST']
        database = app.config['GDB_DATABASE']
        query = app.config['GDB_QUERY']
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

    def getusers(self, orderby=None, order="asc", offset=0, limit=1000):
        """
        Gets and returns a detached user objects for all users in
        specified order and limit.

        Args:
            orderby (str): Name of field to sort by.
                Defaults to None.
            order (str): How to order, 'asc' for acsending,
                'desc' for descending. Defaults to "asc"
            offset (int): How many rows to skip of query.
                Defaults to 0.
            limit (int): How many rows to return of query.
                Defaults to 1000.
        Returns:
            The user model objects in specified order and ammounts.
            Total number of results that match criteria.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Query all users
            query = session.query(User)
            # Order query depending on order parameters
            if(orderby and hasattr(User, orderby) and order == "asc"):
                query = query.order_by(asc(getattr(User, orderby)))
            elif(orderby and hasattr(User, orderby) and order == "desc"):
                query = query.order_by(desc(getattr(User, orderby)))
            else:
                pass
            # Get count
            count = query.count()
            # Filter query by range
            query = query.limit(limit).offset(offset)
            # Get query results
            users = query.all()
            # Detach all share objects from session
            for user in users:
                session.expunge(user)
        # Return share data
        return users, count

    def getuserbyid(self, userID):
        """
        Gets and returns a detached user object based on given ID.

        Args:
            userID (str): The ID of the user to get.
        Returns:
            The user model object for that user.
            None if the user doesn't exist.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Get user
            user = session.query(User).filter(
                   User.userID == userID).first()
            # Check if a user was returned
            if(user is None):
                return None
            # Deteach user from session
            session.expunge(user)
        # Return user
        return user

    def getuserbyusername(self, username):
        """
        Gets and returns a detached user object based on username.

        Args:
            username (str): Username to check database for.
        Returns:
            The user model object for that user.
            None if the user doesn't exist.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Check that username is available. If not, return false.
            user = session.query(User).filter(
                   User.username == username).first()
            # Check if a user was returned
            if(user is None):
                return None
            # Deteach user from session
            session.expunge(user)
        # Return user
        return user

    def getuserbyemail(self, email):
        """
        Gets and returns a detached user object based on username.

        Args:
            email (str): Email of the user to get.
        Returns:
            The user model object for that user.
            None if the user doesn't exist.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Check that username is available. If not, return false.
            user = session.query(User).filter(
                   User.email == email).first()
            # Check if a user was returned
            if(user is None):
                return None
            # Deteach user from session
            session.expunge(user)
        # Return user
        return user

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
                banned=False,
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

    def verifyadmin(self, username, userpass):
        """
        Verifies if the admin with the given username and password exists.

        Args:
            username (str): Username of admin to verify.
            userpass (str): Password of admin to verify.

        Retruns:
            True if the admin exists and valid password, otherwise false.
            Admin ID if the user exists and valid password, None otherwise.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Initialise password hasher
            ph = PasswordHasher()
            # Query if admin exists
            admin = session.query(Admin).filter(
                   Admin.username == username).first()
            # Check if query returns an admin
            if(admin is not None):
                # Verify whether the password is valid or not
                try:
                    ph.verify(admin.passhash, userpass)
                except VerifyMismatchError:
                    # Password does not match, return false
                    return False, None
                # Check if password needs to be rehashed
                if(ph.check_needs_rehash(admin.passhash)):
                    # Generate new hash
                    rehash = ph.hash(userpass)
                    # Update admin record to include new hash
                    user.passhash = rehash
                # Since admin exists and password is valid, return true
                return True, admin.adminID
            else:
                # User doesn't exist, return false
                return False, None

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
                fullname=asxdata['name_full'],
                abbrevname=asxdata['name_abbrev'],
                shortname=asxdata['name_short'],
                description=asxdata['principal_activities'],
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
                    asxdata['primary_share']['change_price']),
                daypricehigh=float(
                    asxdata['primary_share']['day_high_price']),
                daypricelow=float(
                    asxdata['primary_share']['day_low_price']),
                dayvolume=int(
                    asxdata['primary_share']['volume'])
            )
            # Add share to share table
            session.add(share)
            # Return success
            return True

    def getshare(self, issuercode):
        """
        Returns a single share based on the share ID.

        Args:
            issuercode (str): Issuer ID of the share to get.
        Returns:
            Share object with specified issuer code.
            None if there is no share that matches the issuer code.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Get all shares
            share = session.query(Share).get(issuercode)
            # Detach share from session
            session.expunge(share)
        return share

    def getsharepricehistory(self, issuercode):
        """
        Returns the price history of a single share based on the share ID.

        Args:
            issuercode (str): Issuer ID of the share to get price data for.
        Returns:
            All SharePrice objects for that particular share.
            None if the share doesn't exist or if the share has no price data.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Get all shares
            shareprices = session.query(SharePrice).filter(
                SharePrice.issuerID == issuercode).all()
            # Detach all share objects from session
            for shareprice in shareprices:
                session.expunge(shareprice)
        return shareprices

    def getshares(self, orderby=None, order="asc", offset=0, limit=1000):
        """
        Returns a list of all share objects contained in the database.
        Detaches shares from session, so changes cannot be made directly.

        Args:
            orderby (str): Name of field to sort by.
                Defaults to None.
            order (str): How to order, 'asc' for acsending,
                'desc' for descending. Defaults to "asc"
            offset (int): How many rows to skip of query.
                Defaults to 0.
            limit (int): How many rows to return of query.
                Defaults to 1000.
        Returns:
            A list of every share in the database in given order.
            Total number of results that match criteria.


        """
        # Initialse session
        with self.sessionmanager() as session:
            # Get all shares
            query = session.query(Share)
            # Order query depending on order parameters
            if(orderby and hasattr(Share, orderby) and order == "asc"):
                query = query.order_by(asc(getattr(Share, orderby)))
            elif(orderby and hasattr(Share, orderby) and order == "desc"):
                query = query.order_by(desc(getattr(Share, orderby)))
            else:
                pass
            # Get count
            count = query.count()
            # Filter query by range
            query = query.limit(limit).offset(offset)
            # Get query results
            shares = query.all()
            # Detach all share objects from session
            for share in shares:
                session.expunge(share)
        # Return share data
        return shares, count

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
                "currentprice": asxdata['last_price'],
                "marketcapitalisation": asxdata['market_cap'],
                "sharecount": asxdata['number_of_shares'],
                "daychangepercent": asxdata['change_in_percent'],
                "daychangeprice": asxdata['change_price'],
                "daypricehigh": asxdata['day_high_price'],
                "daypricelow": asxdata['day_low_price'],
                "dayvolume": asxdata['volume']
            }

        # Initialse session
        with self.sessionmanager() as session:
            # Iterate over each share and update its values
            for issuerID in share_data:
                # Get share data
                currentprice = float(
                    share_data[issuerID]["currentprice"])
                marketcapitalisation = int(
                    share_data[issuerID]["marketcapitalisation"])
                sharecount = int(
                    share_data[issuerID]["sharecount"])
                daychangepercent = float(
                    share_data[issuerID]["daychangepercent"].strip('%'))/100
                daychangeprice = float(
                    share_data[issuerID]["daychangeprice"])
                daypricehigh = float(
                    share_data[issuerID]['daypricehigh'])
                daypricelow = float(
                    share_data[issuerID]['daypricelow'])
                dayvolume = int(
                    share_data[issuerID]['dayvolume'])
                # Update share field
                share = session.query(Share).get(issuerID)
                share.currentprice = currentprice
                share.marketcapitalisation = marketcapitalisation
                share.sharecount = sharecount
                share.daychangepercent = daychangepercent
                share.daychangeprice = daychangeprice
                share.daypricehigh = daypricehigh
                share.daypricelow = daypricelow
                share.dayvolume = dayvolume
                # Create and add new share price record
                shareprice = SharePrice(
                    issuerID=issuerID,
                    recordtime=datetime.utcnow(),
                    price=currentprice
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
            # Subtract from user balance
            user.balance -= totalprice
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
            # Add to user balance
            user.balance += totalprice
            # Return true for success
            return True

    def getusersharesinfo(self, userID=None,
                          orderby=None, order="asc", offset=0, limit=1000):
        """
        Returns all the shares that a user owns along
        with relevant share information as well.

        Args:
            userID (str): ID of user to get owned shares of.
                Defaults to None.
            orderby (str): Name of field to sort by.
                Defaults to None. Specify 'net' to sort by (profit - loss)
            order (str): How to order, 'asc' for acsending,
                'desc' for descending. Defaults to "asc"
            offset (int): How many rows to skip of query.
                Defaults to 0.
            limit (int): How many rows to return of query.
                Defaults to 1000.
        Returns:
            List of shares that user owns with data from
            usershare and share tables combined.
            Total number of results that match criteria.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Get all shares that the user owns combined with share info
            query = session.query(Usershare, Share).join(Share)
            # If specified, filter by user ID
            if(userID):
                query = query.filter(Usershare.userID == userID)
            # Order query depending on order parameters
            # TODO: Make more effiecent by nesting the if statements
            if(orderby and hasattr(Share, orderby) and order == "asc"):
                query = query.order_by(asc(getattr(Share, orderby)))
            elif(orderby and hasattr(Usershare, orderby) and order == "asc"):
                query = query.order_by(asc(getattr(Usershare, orderby)))
            elif(orderby and hasattr(Share, orderby) and order == "desc"):
                query = query.order_by(desc(getattr(Share, orderby)))
            elif(orderby and hasattr(Usershare, orderby) and order == "desc"):
                query = query.order_by(desc(getattr(Usershare, orderby)))
            elif(orderby == "net" and order == "asc"):
                query = query.order_by(asc(Usershare.profit - Usershare.loss))
            elif(orderby == "net" and order == "desc"):
                query = query.order_by(desc(Usershare.profit - Usershare.loss))
            elif(orderby == "value" and order == "asc"):
                query = query.order_by(
                    asc(Share.currentprice * Usershare.quantity))
            elif(orderby == "value" and order == "desc"):
                query = query.order_by(
                    desc(Share.currentprice * Usershare.quantity))
            else:
                pass
            # Get count
            count = query.count()
            # Filter query by range
            query = query.limit(limit).offset(offset)
            # Get results
            results = query.all()
            # Detach all objects from session
            for result in results:
                for obj in result:
                    session.expunge(obj)
        # Process results into list of combined objects
        usershares = list()
        for result in results:
                # Remove unecessary variables from result dictionaries
                # and combine result dictionaries into one.
                result[0].__dict__.pop('_sa_instance_state', None)
                result[1].__dict__.pop('_sa_instance_state', None)
                combinedres = {**result[0].__dict__, **result[1].__dict__}
                usershares.append(combinedres)
        # Return processed usershares
        return usershares, count

    def gettransactions(self, userID=None, issuerID=None,
                        orderby=None, order="asc", offset=0, limit=1000):
        """
        Get all transactions for a given user and/or share.

        Args:
            userID (str): ID of user to filter transactions by.
                Defaults to None.
            issuerID (str): ID of share to filter transactions by.
                Defaults to None.
            orderby (str): Name of field to sort by.
                Defaults to None.
            order (str): How to order, 'asc' for acsending,
                'desc' for descending. Defaults to "asc"
            offset (int): How many rows to skip of query.
                Defaults to 0.
            limit (int): How many rows to return of query.
                Defaults to 1000.
        Returns:
            List of transaction objects that match filter criteria.
            Total number of results that match criteria.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Query and filter transactions as specified
            query = session.query(Transaction)
            # If user ID is specified, filter by user ID
            if(userID):
                query = query.filter(Transaction.userID == userID)
            # If issuer ID for share is specified, filter by share
            if(issuerID):
                query = query.filter(Transaction.issuerID == issuerID)
            # Order query depending on order parameters
            if(orderby and hasattr(Transaction, orderby) and
               order == "asc"):
                query = query.order_by(asc(getattr(Transaction, orderby)))
            elif(orderby and hasattr(Transaction, orderby) and
                 order == "desc"):
                query = query.order_by(desc(getattr(Transaction, orderby)))
            else:
                pass
            # Get count
            count = query.count()
            # Filter query by range
            query = query.limit(limit).offset(offset)
            # Get query results
            results = query.all()
            # Detach all objects from session
            for result in results:
                session.expunge(result)
        # Return resulting list
        return results, count

    def banuser(self, userID):
        """
        Sets the specified user as banned.

        Args:
            userID (str): User ID of user to ban.
        Returns:
            bool: True if user was successfully banned.
                False if the user doesn't exist.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Get user
            user = session.query(User).get(userID)
            # Check that user exists, returning false if not
            if not user:
                return False
            # Set user as banned
            user.banned = True
        # Return success
        return True

    def unbanuser(self, userID):
        """
        Sets the specified user as not banned.

        Args:
            userID (str): User ID of user to unban.
        Returns:
            bool: True if user was successfully unbanned.
                False if the user doesn't exist.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Get user
            user = session.query(User).get(userID)
            # Check that user exists, returning false if not
            if not user:
                return False
            # Set user as not banned
            user.banned = False
        # Return success
        return True

    def getuserstatistics(self):
        """
        Queries, calculates and returns different user statistics.
        TODO: Potentially move different statistics into seperate methods.

        Returns:
            A dictionary of statistics as follows:
            - Gender distribution as 'gendercounts' dict that contains the
                integer count for each gender, male, female and other.
            - Age group distribution as 'agegroupcounts' dict that contains the
                integer count for each age group of '0to12', '13to17',
                '18to25' and '26toinf'.

        """
        # Initialse session
        with self.sessionmanager() as session:
            # Query all users
            userquery = session.query(User)
            # Get user count
            usercount = userquery.count()

            # Initialise statistics
            statistics = dict()
            # Get gender distribution
            statistics['gendercounts'] = {
                'male': userquery.filter(
                    User.gender == 'M').count(),
                'female': userquery.filter(
                    User.gender == 'F').count(),
                'other': userquery.filter(
                    User.gender == 'O').count()
            }
            # Get age group distribution
            statistics['agegroupcounts'] = {
                '0to12': userquery.filter(
                        User.dob > date.today() - relativedelta(years=13)
                    ).count(),
                '13to17': userquery.filter(
                        User.dob <= date.today() - relativedelta(years=13)
                    ).filter(
                        User.dob > date.today() - relativedelta(years=18)
                    ).count(),
                '18to25': userquery.filter(
                        User.dob <= date.today() - relativedelta(years=18)
                    ).filter(
                        User.dob > date.today() - relativedelta(years=26)
                    ).count(),
                '26toinf': userquery.filter(
                        User.dob <= date.today() - relativedelta(years=26)
                    ).count()
            }

            # Return statistics
            return statistics

if __name__ == "__main__":
    # Initialize API
    gdb = GoogleDatabaseAPI()
    # Add some default stocks
    # stocks = []
    # with open("stock_list.txt") as f:
    #     lines = f.readlines()
    #     for line in lines:
    #         stocks.append(line.strip())
    # for stock in stocks:
    #     gdb.addshare(stock)
