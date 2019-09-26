from gdb_api import GoogleDatabaseAPI
from config import Config
from models import Base, User, Share
import pytest
import unittest
import os


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
        testuser = User(userID=testuserID, firstname="F", lastname="L",
                        email=testemail, dob="2000-01-01",
                        username=testusername, userpass="P1", gender="O",
                        verified=True, banned=False, balance=100)
        assert testuser.userID == 1
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
