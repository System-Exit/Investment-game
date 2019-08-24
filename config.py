import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'PLACEHOLDERSECRETKEY'
    GDB_USERNAME = 'root'
    GDB_PASSWORD = 'RMIT1234!!!'
    GDB_HOST = '127.0.0.1'
    GDB_DATABASE = 'Database'
    GDB_QUERY = ''
