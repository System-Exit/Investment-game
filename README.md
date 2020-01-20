Context/Foreword
================
This is a web application that was built during my time at RMIT and is the capstone project for my group. Including myself, there were 6 group members that worked on this project, though some worked more on the code than others.


Budding Investors
=================
Welcome to Budding Investors! This application has been designed as a way of providing users a way to learn about and practice share market trading in safe sandbox environment that requires no real monetary investment. Once you sign up, you start off with $1,000,000 that you can use to buy and sell whatever shares you like. You can simply invest to your hearts content and potentially see where your investments take you or you can compete against others in the leaderboard to become the best invester there is!

Note: The application is mostly finished, but should still be considered under construction. 


Deploy It Yourself
==================
If you want to develop and use this application elsewhere, we have included a simple guide below:


Prerequisites
-------------
This application requires the following set up in order to be used:
1. A MySQL Database Server: This can either be hosted on your own device/server or on the cloud.
2. A Google cloud project(Optional): If you plan to deploy the application to google cloud, you will need to [set up a new project or use an existsing one here.](https://console.cloud.google.com/project)
3. Google Cloud SDK(Optional): This is required for cloud deployment. [Quickstart guides here.](https://cloud.google.com/sdk/docs/quickstarts)


Configuration
-------------
The application requires some degree of configuration get get up and running.

Here is a list of all the fields in the configuration:
- `SECRET_KEY`: The secret key flask uses for security purposes, make sure to keep this secret. [You can generate one here.](https://www.uuidgenerator.net/version4)
- `DB_DRIVER`: The driver that the application ORM will use. Leave as is unless you know what you are doing.
- `DB_USERNAME`: The username to use when connecting to the database. E.g. "Username123".
- `DB_PASSWORD`: The password to use when connecting to the database. E.g. "Password123.
- `DB_HOST`: The IP of the MySQL server the application will connect to. E.g. "175.58.115.144".
- `DB_PORT`: The port the application will connect to on the MySQL server. E.g. "3306".
- `DB_DATABASE`: The name of the database that the application will use. E.g. "budding-investor-database".
- `DB_QUERY`: A query for the constructed URI, if required. Used when connecting from Google App Engine. E.g. "?unix_socket="

Note: The database settings are used to make up a URI that is used to connect to the database.

Default values for configuration are located in `config.py`. If you plan to run the application locally, you can either modify these default values or set your OS environment variables of the same name to the required values.

Configuration values for cloud deployments are located in `app.yaml`. If you plan to deploy the application to the cloud, you will need to modify these values.


Cloud Deployment
----------------
In order to deploy this application to Google Cloud with full functionality, you will need to do the following:
1. Ensure the `app.yaml` has been configured correctly with the database connection parameters.
2. Ensure your Google Cloud SDK project has been set to the one you want to deploy the application to.
3. Execute the following command in the application directory: `gcloud app deploy app.yaml cron.yaml`. Go through the prompts and wait for the application to successfully deploy. This command will deploy the application and start the share updating cron job.

Once deployed, the application to be ready to use immediately using the link to your Google App Engine appspot.


Local/Server Deployment
-----------------------
For local or server deployment, you will need to satisfy a couple more prerequisites:
1. Python: You will need to download and install python 3.7.3 or later.
2. Python modules: You will need to install the necessary requirements for the application. This can easily be done by executing the following command in the project directory: `pip install -r requirements.txt`.

In order to run the application locally for testing, you will need to do the execute the following command in the project directory: `flask run`. This will run the application at localhost on port 5000.

If you want to run the application on a server using a service such as gunicorn, you should do so using the command: `gunicorn -b :80 main:app`, which will run the application at localhost on port 80.

If you want to have shares updated by a cron job locally, you will need to manually set one up that calls the address appended with '/tasks/updateshares'. The cURL tool should suffice for this purpose. You can also create a python script that calls the `updateshares` method from an initialised instance of the `DatabaseAPI` class from `db_api.py`.


Development and Testing
-----------------------
For development, it is best that you follow the steps to set up the appilication locally, then proceed.

The application uses Python/Flask for the backend and template building of the application, with some JavaScript for the interactive frontend components. Each component of the application is separated as a module ("main" and "admin" for now). If you wish to add new major functionality or separate existing functionality, create a new folder for that module, define it's blueprints and register those blueprints in the `create_app` method. Each module, at minimum, should contain `__init__.py` and `routes.py` files.

The application avoids the use of flask-sqalchemy by separating database interface code from the rest of the code and using sqalchemy directly. This means the database interface code can be reused for future application development, web-based or otherwise.

For local testing, you will need to satisfy some prerequisites:
1. Ensure toy have install general and local prerequisites to get tests working correctly.
2. Install pytest by executing the following command: `pip install pytest`.

In order to run all unit tests, execute the following command in the project directory: `pytest tests.py`.
In order to run a specific test, execute the command: `pytest tests.py::<TEST CLASS>::<TEST METHOD>`.


Miscellaneous Notes
-------------------
As there is no functionality to create an admin account, you must manually add an admin user into the admin table in the application database with the desired username and desired password hashed by using the Argon2 algorithm in python.

While there is currently no way to add new shares via the web UI, you can add them using the `addshare` method from the `DatabaseAPI` class and including the ASX issuer code for the company of the share.
