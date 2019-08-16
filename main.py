from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from config import Config
from flask_login import LoginManager, current_user, login_user, logout_user
from models import User
from forms import UserLoginForm, UserRegistrationForm
from gdb_api import GoogleDatabaseAPI

MyCloud = True

# Load app with bootstrap
app = Flask(__name__)
Bootstrap(app)
login_manager = LoginManager(app)
app.config.from_object(Config)
gdb = GoogleDatabaseAPI()

# Routing for each page
# TODO: Change where routing is handled
@app.route('/')
def index():
    if current_user.is_authenticated:
        # Redirect to dashboard
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    """
    Route for registartion page.
    Processes registration for registration page.

    """
    # Initialise registration form
    form = UserRegistrationForm()
    # Validate and process form data
    if(form.validate_on_submit()):
        # Create new user
        username = form.username.data
        password = form.password.data
        fname = form.fname.data
        lname = form.lname.data
        dob = form.dob.data
        email = form.email.data
        gender = form.gender.data
        # Call database API to create user
        userAdded = gdb.adduser(username, password, fname, lname, email, gender)
        # Check if user was added to database
        if(userAdded):
            # Redirect to index with success message
            flash("Registration successful!", category="message")
            return redirect(url_for('index'))
        else:
            # Redirect to registration with warning message
            flash("Username is already taken!", category="error")
            return redirect(url_for('registration'))
    # Render template
    return render_template('registration.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect to dashboard
        return redirect(url_for('dashboard'))
    # Initialise login form
    form = UserLoginForm()
    # Validate and process form data
    if form.validate_on_submit():
        # Get form data
        username = form.username.data
        password = form.password.data
        # Check if username and password is valid
        valid, user = gdb.verifyuser(username, password)
        if(valid):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", category="error")
            return redirect(url_for('login'))
    # Render template
    return render_template('login.html', form=form)

@login_manager.user_loader
def load_user(userID):
    return gdb.getuser(userID)

@app.route('/logout')
def logout():
    # Log user out
    logout_user()
    # Redirect to index page
    flash("Successfully logged out.", category="message")
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=False)