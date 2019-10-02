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
        # TODO
        pass

    def test_getshare(self):
        # TODO
        pass

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
