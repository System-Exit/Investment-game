import os


class Config(object):
    """
    Configuration class for application.

    """
    SECRET_KEY = os.getenv('SECRET_KEY') or 'PLACEHOLDERSECRETKEY'
    DB_DRIVER = os.getenv('DB_DRIVER') or 'mysql+pymysql'
    DB_USERNAME = os.getenv('DB_USERNAME') or 'root'
    DB_PASSWORD = os.getenv('DB_PASSWORD') or 'RMIT1234!!!'
    DB_HOST = os.getenv('DB_HOST') or '127.0.0.1'
    DB_PORT = os.getenv('DB_PORT') or '3319'
    DB_DATABASE = os.getenv('DB_DATABASE') or 'Database'
    DB_QUERY = os.getenv('DB_QUERY') or ""
