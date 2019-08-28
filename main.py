from flask import (Flask, render_template, request,
                   redirect, url_for, flash, jsonify)
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, login_user, logout_user
from config import Config
from models import User
from forms import UserLoginForm, UserRegistrationForm, BuyShareForm
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
@app.route('/index')
def index():
    """
    Handles landing page, which provides users links to register of login.

    """
    if current_user.is_authenticated:
        # Redirect to dashboard
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    """
    Handles registration for registration page.
    Provides user a form to input registration information.

    """
    # Checks if user is already logged in
    if current_user.is_authenticated:
        # Redirect to dashboard
        return redirect(url_for('dashboard'))
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
        userAdded = gdb.adduser(username, password, fname,
                                lname, email, dob, gender)
        # Check if user was added to database
        if(userAdded):
            # Redirect to index with success message
            flash("Registration successful!", category="success")
            return redirect(url_for('index'))
        else:
            # Redirect to registration with warning message
            flash("Username is already taken!", category="error")
            return redirect(url_for('registration'))
    # Render template
    return render_template('registration.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login for login page.
    Procides user with a login form and checks that input matches a valid user.

    """
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
        valid, userID = gdb.verifyuser(username, password)
        if(valid):
            with gdb.sessionmanager() as session:
                user = gdb.getuser(session, userID)
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
    """
    Handles logging out for user.

    """
    # Log user out if they are authenticated
    if current_user.is_authenticated:
        logout_user()
        # Redirect to index page
        flash("Successfully logged out.", category="success")
    # Redirect back to index
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    """
    Handles and displays dashboard for user.

    """
    # Redirect user to index if they are not logged in
    if not current_user.is_authenticated:
        # Redirect to index
        return redirect(url_for('index'))
    # Get current user
    user = current_user
    return render_template('dashboard.html', user=user)


@app.route('/shares')
def sharelist():
    """
    Displays current values for all shares.

    """
    shares = gdb.getshares()
    return render_template('shares.html', shares=shares)


@app.route('/tasks/updateshares')
def sharesupdate():
    """
    Update shares database.

    """
    # Call database to get new share data
    gdb.updateshares()
    # Return a success response
    return jsonify(success=True)


@app.route('/buyshare', methods=['GET', 'POST'])
def buyshare():
    """
    Buy share for the user.

    """
    # Checks if user is logged in
    if not current_user.is_authenticated:
        # Redirect to login if the user is not authenticated
        flash("Logged in user only.", category="error")
        return redirect(url_for('login'))
    # Initialise buy share form
    form = BuyShareForm()
    # Validate and process form data
    if(form.validate_on_submit()):
        # Buys shares
        issuerID = form.sharecode.data
        quantity = form.quantity.data
        userID = 1
        # Call buyshare API
        buyshare = gdb.buyshare(userID, issuerID, quantity)
        if(buyshare):
            # Redirect to index with success message
            flash("Buyshare successful!", category="success")
            return redirect(url_for('dashboard'))
        else:
            # Redirect to registration with warning message
            flash("Buyshare unsuccessful!", category="error")
            return redirect(url_for('index'))

    return render_template('buyshare.html', form=form)

# Run the app
if __name__ == '__main__':
    app.run(debug=False)
