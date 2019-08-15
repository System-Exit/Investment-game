from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from config import Config
from flask_login import current_user, login_user
from models import User
from forms import UserLoginForm, UserRegistrationForm

MyCloud = True

# Load app with bootstrap
app = Flask(__name__)
app.config.from_object(Config)
Bootstrap(app)

if MyCloud:
    HOST = "35.201.8.54"
    USER = "root"
    PASSWORD = "RMIT1234!!!"
    DATABASE = "USER"
else:
    HOST = ""
    USER = "root"
    PASSWORD = "Bondi2Beach"
    DATABASE = "Library"

SQLALCHEMY_DATABASE_URI = "mysql://{}:{}@{}/{}".format(USER, PASSWORD, HOST, DATABASE)


# Routing for each page
# TODO: Change where routing is handled
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    """
    Route for registartion page.
    Processes registration for registration page.
    TODO: Consider moving the logic for this elsewhere later

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
        # TODO: Call database API to create user
        # Redirect to index
        return redirect(url_for('index'))
    # Render template
    return render_template('registration.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect to index
        return redirect(url_for('index'))
    # Initialise login form
    form = UserLoginForm()
    # Validate and process form data
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        return redirect(url_for('index'))
    # Render template
    return render_template('login.html', form=form)

# Run the app
if __name__ == '__main__':
    app.run(debug=False)