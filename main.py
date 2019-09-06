from flask import (Flask, render_template, request,
                   redirect, url_for, flash, jsonify, abort)
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, login_user, logout_user
from config import Config
from models import User
from forms import (UserLoginForm, UserRegistrationForm,
                   BuyShareForm, SellShareForm)
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
        # Get user registration data
        username = form.username.data
        password = form.password.data
        fname = form.fname.data
        lname = form.lname.data
        dob = f"{form.byear.data}-{form.bmonth.data}-{form.bday.data}"
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
            flash("Registration unsuccessful!", category="error")
            return redirect(url_for('registration'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, category="error")
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
            user = gdb.getuserbyid(userID)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", category="error")
            return redirect(url_for('login'))
    # Render template
    return render_template('login.html', form=form)


@login_manager.user_loader
def load_user(userID):
    return gdb.getuserbyid(userID)


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


@app.route('/portfolio', methods=['GET'])
def portfolio():
    # Redirect user to index if they are not logged in
    if not current_user.is_authenticated:
        # Redirect to login if the user is not authenticated
        flash("Logged in user only.", category="error")
        return redirect(url_for('login'))
    # Get user info
    user = current_user

    # Get field to order by for displaying shares
    if(request.args.get('orderby')):
        orderby = request.args.get('orderby')
    else:
        orderby = None
    # Get order for displaying shares
    if(request.args.get('order')):
        order = request.args.get('order')
    else:
        order = "asc"
    # Get the page of shares to display and calculate offset
    # TODO: DEFINE LIMIT IN A CONFIG
    limit = 10
    if(request.args.get('page')):
        offset = 10*(int(request.args.get('page'))-1)
    else:
        offset = 0
    # Get processed usershare info
    usershares, sharecount = gdb.getusersharesinfo(
        userID=user.userID,
        orderby=orderby,
        order=order,
        offset=offset,
        limit=limit)

    # Render template
    return render_template('portfolio.html', user=user,
                           usershares=usershares,
                           sharecount=sharecount,
                           countperpage=10)


@app.route('/sharelist', methods=['GET'])
def sharelist():
    """
    Displays current values for all shares.

    """
    if not current_user.is_authenticated:
        # Redirect to login if the user is not authenticated
        flash("Logged in user only.", category="error")
        return redirect(url_for('login'))
    # Get field to order by for displaying shares
    if(request.args.get('orderby')):
        orderby = request.args.get('orderby')
    else:
        orderby = None
    # Get order for displaying shares
    if(request.args.get('order')):
        order = request.args.get('order')
    else:
        order = "asc"
    # Get the page of shares to display and calculate offset
    # TODO: DEFINE LIMIT IN A CONFIG
    limit = 10
    if(request.args.get('page')):
        offset = 10*(int(request.args.get('page'))-1)
    else:
        offset = 0
    # Get shares
    shares, sharecount = gdb.getshares(
        orderby=orderby,
        order=order,
        offset=offset,
        limit=limit)

    # Render template
    return render_template('sharelist.html', shares=shares,
                           sharecount=sharecount,
                           countperpage=10)


@app.route('/share/<issuerID>',  methods=['GET'])
def share(issuerID):
    """
    Displays share information.

    """
    if not current_user.is_authenticated:
        # Redirect to login if the user is not authenticated
        flash("Logged in user only.", category="error")
        return redirect(url_for('login'))

    # Initialise buy and sell share forms
    buyform = BuyShareForm()
    sellform = SellShareForm()

    # Get share information
    share = gdb.getshare(issuerID)
    # If the share does not exist, abort with 404 error
    if(share is None):
        abort(404)
    # Get share price history
    sharepricehistory = gdb.getsharepricehistory(issuerID)

    # Get field to order by for displaying shares
    if(request.args.get('orderby')):
        orderby = request.args.get('orderby')
    else:
        orderby = "datetime"
    # Get order for displaying shares
    if(request.args.get('order')):
        order = request.args.get('order')
    else:
        order = "desc"
    # Get the page of shares to display and calculate offset
    # TODO: DEFINE LIMIT IN A CONFIG
    limit = 10
    if(request.args.get('page')):
        offset = 10*(int(request.args.get('page'))-1)
    else:
        offset = 0
    # Get share transaction history for user
    transactions, transcount = gdb.gettransactions(
        userID=current_user.userID,
        issuerID=share.issuerID,
        orderby=orderby,
        order=order,
        offset=offset,
        limit=limit)

    # Render template for share page
    return render_template('share.html', share=share,
                           sharepricehistory=sharepricehistory,
                           buyform=buyform, sellform=sellform,
                           transactions=transactions, transcount=transcount)


@app.route('/buyshares', methods=['GET', 'POST'])
def buyshares():
    # Checks if user is logged in
    if not current_user.is_authenticated:
        # Redirect to login if the user is not authenticated
        flash("Logged in user only.", category="error")
        return redirect(url_for('login'))
    # Initialise buy form
    buyform = BuyShareForm()
    # Validate and process form data
    if(buyform.validate_on_submit()):
        # Buys shares
        issuerID = buyform.buysharecode.data
        quantity = buyform.buyquantity.data
        userID = current_user.userID
        # Call buyshare API
        buyshare = gdb.buyshare(userID, issuerID, quantity)
        if(buyshare):
            # Flash with success message
            flash("Share purchase successful!", category="success")
        else:
            # Flash with warning message
            flash("Share purchase unsuccessful!", category="error")
    # Redirect to reffering page or dashboard
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/sellshares', methods=['GET', 'POST'])
def sellshares():
    # Checks if user is logged in
    if not current_user.is_authenticated:
        # Redirect to login if the user is not authenticated
        flash("Logged in user only.", category="error")
        return redirect(url_for('login'))
    # Initialise buy and sell share forms
    sellform = SellShareForm()
    # Validate and process form data
    if(sellform.validate_on_submit()):
        # Buys shares
        issuerID = sellform.sellsharecode.data
        quantity = sellform.sellquantity.data
        userID = current_user.userID
        # Call buyshare API
        sellshare = gdb.sellshare(userID, issuerID, quantity)
        if(sellshare):
            # Flash with success message
            flash("Share sale successful!", category="success")
        else:
            # Flash with warning message
            flash("Share sale unsuccessful!", category="error")
    # Redirect to reffering page or dashboard
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/tasks/updateshares')
def sharesupdate():
    """
    Update shares database.

    """
    # Call database to get new share data
    gdb.updateshares()
    # Return a success response
    return jsonify(success=True)

# Run the app
if __name__ == '__main__':
    app.run(debug=False)
