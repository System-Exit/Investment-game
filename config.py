import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'PLACEHOLDERSECRETKEY'
    GDB_USERNAME = 'root' 
    GDB_PASSWORD = 'RMIT1234!!!'
    GDB_HOST = '35.189.52.142'
    GDB_DATABASE = 'database'