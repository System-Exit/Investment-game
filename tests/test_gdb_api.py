from gdb_api import GoogleDatabaseAPI
from config import Config
from models import Base
import unittest
import os


class TestConfig(Config):
    """
    Configuration class for testing purposes.

    """
    SECRET_KEY = os.getenv('TEST_SECRET_KEY') or 'PLACEHOLDERSECRETKEY'
    GDB_USERNAME = os.getenv('TEST_GDB_USERNAME') or 'root'
    GDB_PASSWORD = os.getenv('TEST_GDB_PASSWORD') or 'RMIT1234!!!'
    GDB_HOST = os.getenv('TEST_GDB_HOST') or '127.0.0.1'
    GDB_DATABASE = os.getenv('TEST_GDB_DATABASE') or 'TestDatabase'
    GDB_QUERY = os.getenv('TEST_GDB_QUERY') or ''


class TestGoogleDatabaseAPI(unittest.TestCase):
    def setUp(self):
        # Initialise database interface
        self.gdb = GoogleDatabaseAPI(config_class=TestConfig)
        # Create all tables if they don't exist
        Base.metadata.create_all(self.gdb.engine)

    def tearDown(self):
        pass

    def test_one(self):
        # Define test user data
        username = 'testuser'
        password = 'testuser123'
        fname = 'testfirst'
        lname = 'testlast'
        dob = '1998-06-21'
        email = 'test@test.com'
        gender = 'O'
        # Call database API to create user
        userAdded = self.gdb.adduser(username, password, fname,
                                     lname, email, dob, gender)
        # Assert user added is true
        assert userAdded is True
