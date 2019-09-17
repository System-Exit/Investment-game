from flask import (Flask, render_template, request, session,
                   redirect, url_for, flash, jsonify, abort)
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, login_user, logout_user
from config import Config
from models import User
from forms import (UserLoginForm, UserRegistrationForm,
                   BuyShareForm, SellShareForm)
from gdb_api import GoogleDatabaseAPI

MyCloud = True

# Load app and config
app = Flask(__name__)
app.config.from_object(Config)

# Load app modules and interfaces
Bootstrap(app)
login_manager = LoginManager(app)
gdb = GoogleDatabaseAPI()


# Routing for each page
# TODO: Change where routing is handled
@app.route('/')
@app.route('/index')
def index():
    """
    Handles landing page, which provides users links to register of login.

    """
    # Check if user is already logged in
    if current_user.is_authenticated:
        # Redirect to dashboard
        return redirect(url_for('dashboard'))
    # Check if admin is already logged in
    check = checkAdminIsLoggedIn()
    if check is True:
        return redirect(url_for('admindashboard'))

    # Render template
    return render_template('index.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    """
    Handles registration for registration page.
    Provides user a form to input registration information.

    """
    # Check if user is already logged in
    if current_user.is_authenticated:
        # Redirect to dashboard
        return redirect(url_for('dashboard'))
    # Check if admin is already logged in
    check = checkAdminIsLoggedIn()
    if check is True:
        return redirect(url_for('admindashboard'))

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
    # Check if user is already logged in
    if current_user.is_authenticated:
        # Redirect to dashboard
        return redirect(url_for('dashboard'))
    # Check if admin is already logged in
    check = checkAdminIsLoggedIn()
    if check is True:
        return redirect(url_for('admindashboard'))

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
    # Get user object
    user = gdb.getuserbyid(userID)
    # Return user object
    return user


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
    # Check valid user is logged in
    check, redirect = checkUserIsLoggedIn(warnuser=True, getredirect=True)
    if(check is not True):
        return redirect

    # Get current user
    user = current_user
    # Render template
    return render_template('dashboard.html', user=user)


@app.route('/portfolio', methods=['GET'])
def portfolio():
    # Check valid user is logged in
    check, redirect = checkUserIsLoggedIn(warnuser=True, getredirect=True)
    if(check is not True):
        return redirect

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
                           countperpage=limit)


@app.route('/sharelist', methods=['GET'])
def sharelist():
    """
    Displays current values for all shares.

    """
    # Check valid user is logged in
    check, redirect = checkUserIsLoggedIn(warnuser=True, getredirect=True)
    if(check is not True):
        return redirect

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
                           countperpage=limit)


@app.route('/share/<issuerID>',  methods=['GET'])
def share(issuerID):
    """
    Displays share information.

    """
    # Check valid user is logged in
    check, redirect = checkUserIsLoggedIn(warnuser=True, getredirect=True)
    if(check is not True):
        return redirect

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
                           transactions=transactions, transcount=transcount,
                           countperpage=limit)


@app.route('/buyshares', methods=['GET', 'POST'])
def buyshares():
    # Check valid user is logged in
    check, redirect = checkUserIsLoggedIn(warnuser=True, getredirect=True)
    if(check is not True):
        return redirect

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
    # Check valid user is logged in
    check, redirect = checkUserIsLoggedIn(warnuser=True, getredirect=True)
    if(check is not True):
        return redirect

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


@app.route('/admin', methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
def adminlogin():
    """
    Landing and login page for administators.

    """
    # Check if admin is already logged in
    check = checkAdminIsLoggedIn()
    if check is True:
        return redirect(url_for('admindashboard'))

    # Initialise login form
    form = UserLoginForm()
    # Validate and process form data
    if form.validate_on_submit():
        # Get form data
        username = form.username.data
        password = form.password.data
        # Check if username and password is valid
        valid, userID = gdb.verifyadmin(username, password)
        if(valid):
            # Set admin authentication in session
            session['authenticated_admin'] = True
            # Redirect to admin dashboard
            return redirect(url_for('admindashboard'))
        else:
            flash("Invalid username or password.", category="error")
            return redirect(url_for('adminlogin'))
    # Render template
    return render_template('adminlogin.html', form=form)


@app.route('/admin/logout')
def adminlogout():
    """
    Handles logout for admin.

    """
    # Remove session admin authentication
    session.pop('authenticated_admin', None)
    # Redirect to admin login
    return redirect(url_for('adminlogin'))


@app.route('/admin/dashboard')
def admindashboard():
    """
    Displays dashboard for administrator.

    """
    # Check admin is logged in
    check, redirect = checkAdminIsLoggedIn(warnuser=True, getredirect=True)
    if check is not True:
        return redirect

    # Render template
    return render_template('admindashboard.html')


@app.route('/admin/userlist')
def adminuserlist():
    """
    Lists all users for administrator.

    """
    # Check admin is logged in
    check, redirect = checkAdminIsLoggedIn(warnuser=True, getredirect=True)
    if check is not True:
        return redirect

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
    # Get users
    users, usercount = gdb.getusers(
        orderby=orderby,
        order=order,
        offset=offset,
        limit=limit)
    # Render template
    return render_template('adminuserlist.html',
                           users=users,
                           usercount=usercount,
                           countperpage=limit)


@app.route('/admin/user/<userID>')
def adminuser(userID):
    """
    Displays details of a user for an administrator.

    """
    # Check admin is logged in
    check, redirect = checkAdminIsLoggedIn(warnuser=True, getredirect=True)
    if check is not True:
        return redirect

    # Get user based on user ID
    user = gdb.getuserbyid(userID)
    # Render template
    return render_template('adminuser.html', user=user)


@app.route('/admin/user/<userID>/ban')
def banuser(userID):
    # Check admin is logged in
    check, redirect = checkAdminIsLoggedIn(warnuser=True, getredirect=True)
    if check is not True:
        return redirect

    # Ban user based on ID
    result = gdb.banuser(userID)
    # Flash message for whether or not the ban was successful
    if(result):
        flash(f"User {userID} has been banned successfully.",
              category="success")
    else:
        flash(f"User {userID} was not not banned successfuly.",
              category="error")

    # Redirect to reffering page or admin dashboard
    return redirect(request.referrer or url_for('admindashboard'))


@app.route('/admin/user/<userID>/unban')
def unbanuser(userID):
    # Check admin is logged in
    check, redirect = checkAdminIsLoggedIn(warnuser=True, getredirect=True)
    if check is not True:
        return redirect

    # Ban user based on ID
    result = gdb.unbanuser(userID)
    # Flash message for whether or not the ban was successful
    if(result):
        flash(f"User {userID} has been unbanned successfully.",
              category="success")
    else:
        flash(f"User {userID} was not not unbanned successfuly.",
              category="error")

    # Redirect to reffering page or admin dashboard
    return redirect(request.referrer or url_for('admindashboard'))


@app.route('/admin/statistics')
def adminstatistics():
    """
    Lists statistics of userbase to admin.

    """
    # Check admin is logged in
    check, redirect = checkAdminIsLoggedIn(warnuser=True, getredirect=True)
    if check is not True:
        return redirect

    # Get all user statistics
    userstatistics = gdb.getuserstatistics()

    # Render template with statistics
    return render_template('adminstatistics.html',
                           userstatistics=userstatistics)


def checkUserIsLoggedIn(warnuser=False, getredirect=False):
    """
    Helper method for checking if the user is logged in or banned.
    If the user isn't logged in, they are redirected to login page.
    If the user has been banned, redirect them to index.

    Args:
        warnuser (bool): Whether or not to flash warning to user.
            Defaults to False.
        getredirect (bool): Whether or not to include a redirect along with
            the result. Defaults to False.
    Returns:
        True is the user is logged in and is not banned.
        An appropriate redirect if the user is not logged in or banned.

    """
    # Check if user is logged in
    if not current_user.is_authenticated:
        # Flash error if specified
        if warnuser is True:
            flash("Logged in user only.", category="error")
        # Return false and redirect to login if specified
        if getredirect:
            # Redirect to index
            return False, redirect(url_for('login'))
        else:
            return False
    # Check if the user has been banned
    if current_user.banned:
        # Inform the user they are banned if specified
        if warnuser is True:
            flash("You have been banned, please contact an admin.",
                  category="error")
        # Log user out
        logout_user()
        # Return false and a redirect to index if specified
        if getredirect:
            # Redirect to index
            return False, redirect(url_for('index'))
        else:
            return False
    # Flash warning if specified
    if warnuser is True:
        flash("Already logged in.", category="error")
    # Since user is authenticated, return true and no redirect if specified
    if getredirect:
        return True, None
    else:
        return True


def checkAdminIsLoggedIn(warnuser=False, getredirect=False):
    """
    Helper method for checking if an admin is logged in.
    If the admin isn't logged in, they are redirected to login page.
    If the user has been banned, redirect them to index.

    Args:
        warnuser (bool): Whether or not to flash warning to user.
            Defaults to False.
        getredirect (bool): Whether or not to include a redirect along with
            the result. Defaults to False.
    Returns:
        True is the admin is authenticated, false otherwise.
        If getredirect is set to true, an appropriate redirect
            if the user is not authenticated as an admin.

    """
    # Check that admin is logged in
    if ('authenticated_admin' not in session or
       not session['authenticated_admin']):
        # Flash error if specified
        if warnuser is True:
            flash("You must be an admin to access this page.",
                  category="error")
        # Return false and a redirect if specified
        if getredirect:
            return False, redirect(url_for('adminlogin'))
        else:
            return False
        # Redirect to login if the admin is not authenticated
        return redirect(url_for('adminlogin'))
    # Flash warning if specified
    if warnuser is True:
        flash("Already logged in as admin.", category="error")
    # Since admin is authenticated, return true and no redirect if specified
    if getredirect:
        return True, None
    else:
        return True


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
