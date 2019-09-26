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
    DB_USERNAME = os.getenv('TEST_DB_USERNAME') or 'root'
    DB_PASSWORD = os.getenv('TEST_DB_PASSWORD') or 'root'
    DB_HOST = os.getenv('TEST_DB_HOST') or '127.0.0.1'
    DB_PORT = os.getenv('TEST_DB_PORT') or '3307'
    DB_DATABASE = os.getenv('TEST_DB_DATABASE') or 'testdatabase'
    DB_QUERY = os.getenv('TEST_DB_QUERY') or ''


class TestGoogleDatabaseAPI(unittest.TestCase):
    def setUpClass(self):
        # Initialise database interface
        self.gdb = GoogleDatabaseAPI(config_class=TestConfig)
        # Create all tables
        Base.metadata.create_all(self.gdb.engine)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def tearDownClass(self):
        # Delete all tables
        Base.metadata.drop_all(self.gdb.engine)

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
        # Get all users
        users = self.gdb.getusers()
        # Assert that all dummy users are present in database
        for du in self.dummyusers:
            assert any(du.username == u.username for u in users) is True

        # Get user by ID
        user = self.gdb.getuserbyid(self.dummyusers[0].userID)
        # Assert that returned user is correct
        assert user.userID == self.dummyusers[0].userID
        assert user.username == self.dummyusers[0].username

        # Get user by username
        user = self.gdb.getuserbyusername(self.dummyusers[0].username)
        # Assert that returned user is correct
        assert user.userID == self.dummyusers[0].userID
        assert user.username == self.dummyusers[0].username

        # Get user by email
        user = self.gdb.getuserbyemail(self.dummyusers[0].email)
        # Assert that returned user is correct
        assert user.userID == self.dummyusers[0].userID
        assert user.username == self.dummyusers[0].username

