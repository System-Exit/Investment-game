"""Initialize app."""
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, login_user, logout_user
from db_api import DatabaseAPI
from config import Config


# Initialise flask plugins
bootstrap = Bootstrap()
login_manager = LoginManager()
# Initialise Database Interface
gdb = DatabaseAPI(Config)


def create_app(config_class=Config):
    """
    Construct the core application.

    """
    # Load app and config
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialise database schema if not already done
    gdb.createtables()

    # Initialise plugins
    bootstrap.init_app(app)
    login_manager.init_app(app)

    # Import parts of our application
    from app.main import bp as main_bp
    from app.admin import bp as admin_bp

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Return the app
    return app
