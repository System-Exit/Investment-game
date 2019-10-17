Budding Investors
=================
Welcome to Budding Investors! This application has been designed as a way of providing users a way to learn about and practice share market trading in safe sandbox environment that requires no real monetary investment. Once you sign up, you start off with $1,000,000 that you can use to buy and sell whatever shares you like. You can simply invest to your hearts content and potentially see where your investments take you or you can compete against others in the leaderboard to become the best invester there is!

Links
-----
Budding Investors Website: https://budding-investors-248807.appspot.com/

Github repository: https://github.com/s3606685-declan/Investment-game


Deploy your own version
=======================
If you want to develop and use this application elsewhere, we have included a simple guide below:


Prerequisites
-------------
This application requires the following set up in order to be used:
1. A MySQL Database Server: This can either be hosted on your own device/server or on the cloud.
2. A Google cloud project(Optional): If you plan to deploy the application to google cloud, you will need to [set up a new project or use an existsing one here.](https://console.cloud.google.com/project)
2. Google Cloud SDK(Optional): This is required for cloud deployment. [Quickstart guides here.](https://cloud.google.com/sdk/docs/quickstarts)


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
1. Ensure your Google Cloud SDK project has been set to the one you want to deploy the application to.
2. Execute the following command in the application directory: `gcloud app deploy app.yaml cron.yaml`. Go through the prompts and wait for the application to successfully deploy.

Once deployed, the application to be ready to use immediately.


Local/Server Deployment
-----------------------
TODO: Will be available soon!
