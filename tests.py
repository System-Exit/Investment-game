from gdb_api import GoogleDatabaseAPI
from config import Config
from models import Base, User, Share, Admin
from argon2 import PasswordHasher
import pytest
import unittest
import os
import random
import string


class TestConfig(Config):
    """
    Configuration class for testing purposes.

    """
    SECRET_KEY = os.getenv('TEST_SECRET_KEY') or 'PLACEHOLDERSECRETKEY'
    """
    DB_USERNAME = os.getenv('TEST_DB_USERNAME') or 'root'
    DB_PASSWORD = os.getenv('TEST_DB_PASSWORD') or 'root'
    DB_HOST = os.getenv('TEST_DB_HOST') or '127.0.0.1'
    DB_PORT = os.getenv('TEST_DB_PORT') or '3307'
    DB_DATABASE = os.getenv('TEST_DB_DATABASE') or 'testdatabase'
    DB_QUERY = os.getenv('TEST_DB_QUERY') or ''
    """
    DB_DRIVER = os.getenv('TEST_DB_DRIVER') or "mysql+pymysql"
    DB_USERNAME = os.getenv('TEST_DB_USERNAME') or 'root'
    DB_PASSWORD = os.getenv('TEST_DB_PASSWORD') or 'RMIT1234!!!'
    DB_HOST = os.getenv('TEST_DB_HOST') or '127.0.0.1'
    DB_PORT = os.getenv('TEST_DB_PORT') or '3306'
    DB_DATABASE = os.getenv('TEST_DB_DATABASE') or 'TestDatabase'
    DB_QUERY = os.getenv('TEST_DB_QUERY') or ''


class TestGoogleDatabaseAPI(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Initialise database interface
        self.gdb = GoogleDatabaseAPI(config_class=TestConfig)

    def setUp(self):
        # Create all tables
        Base.metadata.create_all(self.gdb.engine)

    def tearDown(self):
        # Delete all tables
        Base.metadata.drop_all(self.gdb.engine)

    @classmethod
    def tearDownClass(self):
        pass

    def test_adduser(self):
        # Add valid users and assert they were added successfully
        assert self.gdb.adduser(
            "user1",
            "password1",
            "fname1",
            "lname1",
            "email1@test.com",
            "1950-06-15",
            "O"
        ) is True
        # Ensure that we cannot add user with same username
        assert self.gdb.adduser(
            "user1",
            "password2",
            "fname2",
            "lname2",
            "email2@test.com",
            "1950-06-15",
            "O"
        ) is False
        # Ensure that we cannot add user with same email
        assert self.gdb.adduser(
            "username2",
            "password2",
            "fname2",
            "lname2",
            "email1@test.com",
            "1950-06-15",
            "O"
        ) is False

    def test_getusers(self):
        # Create test user
        testuserID = 1
        testusername = "U1"
        testemail = "E1"
        testuser = self.generatetestuser(
            userID=testuserID, email=testemail, username=testusername)
        # Add user to database directly
        with self.gdb.sessionmanager() as session:
            session.add(testuser)
        # Get all users
        users, num = self.gdb.getusers()
        # Assert that user is present in returned users list
        assert users[0].userID == testuserID

        # Get user by ID
        user = self.gdb.getuserbyid(testuserID)
        # Assert that returned user is correct
        assert user.userID == testuserID

        # Get user by username
        user = self.gdb.getuserbyusername(testusername)
        # Assert that returned user is correct
        assert user.userID == testuserID

        # Get user by email
        user = self.gdb.getuserbyemail(testemail)
        # Assert that returned user is correct
        assert user.userID == testuserID

    def test_verifyuser(self):
        # Create user
        username = "TestUser"
        userpass = "TestPass123"
        wrongpass = "NotTestPass123"
        testuser = self.generatetestuser(username=username, userpass=userpass)
        # Add user to database directly
        with self.gdb.sessionmanager() as session:
            session.add(testuser)
        # Assert that user is verified with correct password
        verified, userID = self.gdb.verifyuser(username, userpass)
        assert verified is True
        # Assert that user is not verified with incorrect password
        verified, userID = self.gdb.verifyuser(username, wrongpass)
        assert verified is False

    def test_verifyadmin(self):
        # Create admin
        username = "testmin"
        rightpass = "testpass"
        wrongpass = "untestpass"
        admin = Admin(
            username=username,
            passhash=PasswordHasher().hash(rightpass)
        )
        # Add admin to database directly
        with self.gdb.sessionmanager() as session:
            session.add(admin)
        # Assert that user is verified with correct password
        verified, userID = self.gdb.verifyadmin(username, rightpass)
        assert verified is True
        # Assert that user is not verified with incorrect password
        verified, userID = self.gdb.verifyadmin(username, wrongpass)
        assert verified is False

    def test_addshare(self):
        # Attempt to add valid ASX share and assert true
        issuerID = "ASX"
        success = self.gdb.addshare(issuerID)
        assert success is True
        # Attempt to add already added share and assert false
        success = self.gdb.addshare(issuerID)
        assert success is False
        # Attempt to add invalid share to database and assert false
        notissuerID = "000"
        success = self.gdb.addshare(notissuerID)
        assert success is False
        # Get shares from database directly
        with self.gdb.sessionmanager() as session:
            # Assert that share exists with correct issuer ID
            share = session.query(Share).get(issuerID)
            assert share.issuerID == issuerID
            # Assert that share with incorrect issuer ID doesn't exist
            share = session.query(Share).get(notissuerID)
            assert share is None

    def test_getshare(self):
        # Create share
        issuerID = "TRU"
        notissuerID = "FAL"
        share = self.generatetestshare(issuerID=issuerID)
        # Add share directly to database
        with self.gdb.sessionmanager() as session:
            session.add(share)
        # Get share
        share = self.gdb.getshare(issuerID)
        # Assert that share was returned with correct ID
        assert share.issuerID == issuerID
        # Attempt to get non-existant share
        share = self.gdb.getshare(notissuerID)
        # Assert that None was returned
        assert share is None

    def test_getshares(self):
        # TODO
        pass

    def test_getsharepricehistory(self):
        # TODO
        pass

    def test_updateshares(self):
        # TODO
        pass

    def test_buyshare(self):
        # TODO
        pass

    def test_sellshare(self):
        # TODO
        pass

    def test_getusershareinfo(self):
        # TODO
        pass

    def test_gettransactions(self):
        # TODO
        pass

    def test_banuser(self):
        # Create unbanned user
        userID = 1
        banned = False
        user = self.generatetestuser(userID=userID, banned=banned)
        # Add user to database directly
        with self.gdb.sessionmanager() as session:
            session.add(user)
        # Ban the user
        self.gdb.banuser(userID=userID)
        # Assert that the user is banned
        with self.gdb.sessionmanager() as session:
            user = session.query(User).get(userID)
            banned = user.banned
        assert banned is True

    def test_unbanuser(self):
        # Create unbanned user
        userID = 1
        banned = True
        user = self.generatetestuser(userID=userID, banned=banned)
        # Add user to database directly
        with self.gdb.sessionmanager() as session:
            session.add(user)
        # Ban the user
        self.gdb.unbanuser(userID=userID)
        # Assert that the user is banned
        with self.gdb.sessionmanager() as session:
            user = session.query(User).get(userID)
            banned = user.banned
            assert banned is False

    def test_getuserstatistics(self):
        # TODO
        pass

    def generatetestuser(self, userID=None, firstname=None, lastname=None,
                         email=None, dob=None, gender=None, username=None,
                         userpass=None, verified=None, banned=None,
                         balance=None, hashpassword=True):
        """
        Helper method for creating a test user that with specified
        attributes. If a user attribute is not defined, a random value will
        be generated and assigned instead.

        Args:
            All attributes of User object, all default to none and will
                be generated for the user unless assigned a value. Unless
                one is specified, the userID will not be generated here.
            hashpassword (bool): Whether or not to hash the user's password.
                Defaults to True.
        Returns:
            A user object with the given and generated attributes.

        """
        # Generate values for each attribute if one is not assigned.
        if not firstname:
            firstname = ''.join(random.choices(string.ascii_lowercase, k=10))
        if not lastname:
            lastname = ''.join(random.choices(string.ascii_lowercase, k=10))
        if not email:
            part = ''.join(random.choices(string.ascii_lowercase, k=10))
            domain = ''.join(random.choices(string.ascii_lowercase, k=10))
            email = f"{part}@{domain}.com"
        if not dob:
            year = random.randint(1900, 2015)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            dob = f"{year}-{month}-{day}"
        if not gender:
            gender = ''.join(random.choices(["M", "F", "O"], k=1))
        if not username:
            username = ''.join(random.choices(string.ascii_lowercase, k=15))
        if not userpass:
            userpass = ''.join(random.choices(
                string.ascii_letters + string.digits, k=10))
        if not verified:
            verified = random.choices([True, False])[0]
        if not banned:
            banned = random.choices([True, False])[0]
        if not balance:
            balance = random.randint(1000, 10000000)
        # If hash pass is set, hash the userpass
        if hashpassword:
            userpass = PasswordHasher().hash(userpass)
        # Create user
        generateduser = User(
            userID=userID,
            firstname=firstname,
            lastname=lastname,
            email=email,
            dob=dob,
            username=username,
            userpass=userpass,
            gender=gender,
            verified=verified,
            banned=banned,
            balance=balance)
        # Return generated user
        return generateduser

    def generatetestshare(self, issuerID=None, fullname=None, shortname=None,
                          abbrevname=None, description=None,
                          industrysector=None, currentprice=None,
                          marketcapitalisation=None, sharecount=None,
                          daychangepercent=None, daychangeprice=None,
                          daypricehigh=None, daypricelow=None, dayvolume=None):
        """
        Helper method for creating a test share with specified attributes.
        If a share attribute is not defined, a random value will be generated
        and assigned instead.

        Args:
            All attributes of Share object, all default to none and will
                be generated for the user unless assigned a value. Unless
                one is specified, the userID will not be generated here.
        Returns:
            A user object with the given and generated attributes.

        """
        # Generate values for each attribute if one is not assigned.
        if not issuerID:
            issuerID = ''.join(random.choices(string.ascii_uppercase, k=3))
        if not fullname:
            fullname = ''.join(random.choices(string.ascii_lowercase, k=10))
        if not shortname:
            shortname = ''.join(random.choices(string.ascii_lowercase, k=10))
        if not abbrevname:
            abbrevname = ''.join(random.choices(string.ascii_lowercase, k=10))
        if not description:
            description = ''.join(random.choices(string.ascii_lowercase, k=50))
        if not industrysector:
            industrysector = ''.join(random.choices(
                string.ascii_lowercase, k=10))
        if not currentprice:
            currentprice = round(random.uniform(1.0, 1000.0), 2)
        if not marketcapitalisation:
            marketcapitalisation = random.randint(1000000, 1000000000)
        if not sharecount:
            sharecount = random.randint(1000000, 1000000000)
        if not daychangepercent:
            daychangepercent = round(random.uniform(-1.0, 1.0), 2)
        if not daychangeprice:
            daychangeprice = round(random.uniform(1.0, 100.0), 2)
        if not daypricehigh:
            daypricehigh = round(random.uniform(currentprice, 1000.0), 2)
        if not daypricelow:
            daypricelow = round(random.uniform(1.0, currentprice), 2)
        if not dayvolume:
            dayvolume = random.randint(1000, 10000000)
        # Create share
        share = Share(
            issuerID=issuerID,
            fullname=fullname,
            abbrevname=abbrevname,
            shortname=shortname,
            description=description,
            industrysector=industrysector,
            currentprice=currentprice,
            marketcapitalisation=marketcapitalisation,
            sharecount=sharecount,
            daychangepercent=daychangepercent,
            daychangeprice=daychangeprice,
            daypricehigh=daypricehigh,
            daypricelow=daypricelow,
            dayvolume=dayvolume
        )
        # Return generated share
        return share