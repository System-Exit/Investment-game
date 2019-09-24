from gdb_api import GoogleDatabaseAPI
from config import Config
from models import Base, User
import pytest
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
        # Create all tables
        Base.metadata.create_all(self.gdb.engine)

    def tearDown(self):
        # Delete all tables
        Base.metadata.drop_all(self.gdb.engine)

    def test_adduser(self):
        # Get dummy users
        users = self.dummyvalidusers()
        # Iterate over each user
        for user in users:
            # Add user
            userAdded = self.gdb.adduser(
                user.username,
                user.userpass,
                user.firstname,
                user.lastname,
                user.email,
                user.dob,
                user.gender
            )
            # Check that user was successfully added
            assert userAdded is True

        # Ensure that we cannot add user with same username
        assert self.gdb.adduser(
            users[0].username,
            "password",
            "fname",
            "lname",
            "email@test.com",
            "1950-06-15",
            "O"
        ) is False

        # Ensure that we cannot add user with same email
        assert self.gdb.adduser(
            "username",
            "password",
            "fname",
            "lname",
            users[0].email,
            "1950-06-15",
            "O"
        ) is False

    def test_getuser(self):
        # Get dummy users
        users = self.dummyvalidusers()

    def dummyvalidusers(self):
        """
        Returns dummy users that are valid.

        """
        # Define valid users
        users = list()
        users.append(User(
            username='alice123',
            userpass='Madhatter123',
            firstname='Alice',
            lastname='Liddell',
            dob='1998-06-21',
            email='alice@wonderland.com',
            gender='F'
        ))
        users.append(User(
            username='bobby123',
            userpass='BobbyJenkins123',
            firstname='Bob',
            lastname='Jenkins',
            dob='1976-04-26',
            email='bob@gmail.com',
            gender='M'
        ))
        # Return users
        return users
