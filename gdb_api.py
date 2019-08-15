from config import Config
#import sqlalchemy as db
import pymysql as db


class GoogleDatabaseAPI:
    """
    API class for handling calls to google cloud SQL database

    """
    def __init__(self):
        """
        Initialise connection to database and setup API

        """
        # drivername = 'mysql+pymysql'
        username = Config.GDB_USERNAME
        password = Config.GDB_PASSWORD
        host = Config.GDB_HOST
        database = Config.GDB_DATABASE
        # SQLAlchemy code
        # db.create_engine('%s://%s:%s@%s/%s' % (drivername, username, password, host, database))
        # conn = engine.connect()
        # meta = db.MetaData()
        # SQL code
        conn = db.Connect(host=host, user=username, password=password, db=database)
        

if __name__ == "__main__":
    GoogleDatabaseAPI()
        