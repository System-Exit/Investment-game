from flask import (Flask, render_template, request, session,
                   redirect, url_for, flash, jsonify, abort)
from flask_login import LoginManager, current_user, login_user, logout_user
from models import User
from functools import wraps
from app import gdb, login_manager
from app.main import bp
from app.main.forms import (UserLoginForm, UserRegistrationForm,
                            BuyShareForm, SellShareForm)
from datetime import datetime, timedelta, timezone


def user_login_required(f):
    """
    Decorator for routes that require user logins.

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # Flash warning that user login is required
            flash("Logged in user only.", category="error")
            # Return redirect to login
            return redirect(url_for('main.login'))
        if current_user.banned:
            # Log user out so they can't access their account
            logout_user()
            # Flash warning that user has been banned
            flash("You have been banned, please contact an admin.",
                  category="error")
            # Return redirect to index
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def admin_login_required(f):
    """
    Decorator for routes that require admin logins.

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if ('authenticated_admin' not in session or
           not session['authenticated_admin']):
            # Flash warning that admin login is required
            flash("You must be an admin to access this page.",
                  category="error")
            # Return redirect
            return redirect(url_for('main.adminlogin'))
        return f(*args, **kwargs)
    return decorated_function


# Routing for each page
@bp.route('/')
@bp.route('/')
def index():
    """
    Handles landing page, which provides users links to register of login.

    """
    # Render template
    return render_template('index.html')


@bp.route('/registration', methods=['GET', 'POST'])
def registration():
    """
    Handles registration for registration page.
    Provides user a form to input registration information.

    """
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
            return redirect(url_for('main.index'))
        else:
            # Redirect to registration with warning message
            flash("Registration unsuccessful!", category="error")
            return redirect(url_for('main.registration'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, category="error")
    # Render template
    return render_template('registration.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login for login page.
    Procides user with a login form and checks that input matches a valid user.

    """
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
            return redirect(url_for('main.dashboard'))
        else:
            flash("Invalid username or password.", category="error")
            return redirect(url_for('main.login'))
    # Render template
    return render_template('login.html', form=form)


@login_manager.user_loader
def load_user(userID):
    # Get user object
    user = gdb.getuserbyid(userID)
    # Return user object
    return user


@bp.route('/logout')
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
    return redirect(url_for('main.index'))


@bp.route('/dashboard')
@user_login_required
def dashboard():
    """
    Handles and displays dashboard for user.

    """
    # Get current user
    user = current_user
    # Render template
    return render_template('dashboard.html', user=user,
                           userbalance=current_user.balance)


@bp.route('/portfolio', methods=['GET'])
@user_login_required
def portfolio():
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
                           countperpage=limit,
                           userbalance=current_user.balance)


@bp.route('/sharelist', methods=['GET'])
@user_login_required
def sharelist():
    """
    Displays current values for all shares.

    """
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
                           countperpage=limit,
                           userbalance=current_user.balance)


@bp.route('/share/<issuerID>',  methods=['GET'])
@user_login_required
def share(issuerID):
    """
    Displays share information.

    """
    # Initialise buy and sell share forms
    buyform = BuyShareForm()
    sellform = SellShareForm()

    # Get share information
    share = gdb.getshare(issuerID)
    # If the share does not exist, abort with 404 error
    if(share is None):
        abort(404)

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
                           buyform=buyform, sellform=sellform,
                           transactions=transactions, transcount=transcount,
                           countperpage=limit,
                           userbalance=current_user.balance)


@bp.route('/buyshares', methods=['GET', 'POST'])
@user_login_required
def buyshares():
    """
    Handles the purchase of shares.

    """
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
    return redirect(request.referrer or url_for('main.dashboard'))


@bp.route('/sellshares', methods=['GET', 'POST'])
@user_login_required
def sellshares():
    """
    Handles the selling of shares.

    """
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
    return redirect(request.referrer or url_for('main.dashboard'))


@bp.route('/updates/pricegraph', methods=['POST'])
def sharepricehistorydata():
    # Get JSON request data
    data = request.get_json()
    issuerID = data.get('issuerID')
    endtime = datetime.now()
    starttime = endtime - timedelta(data.get('days'))
    # Get share price history for given share and period
    sharepricehistory = gdb.getsharepricehistory(
        issuerID=issuerID, starttime=starttime, endtime=endtime)
    # Parse results into dictionary
    data = list()
    for shareprice in sharepricehistory:
        # Change timezone of recording time
        time = str(shareprice.time.replace(
            tzinfo=timezone.utc).astimezone(tz=None))
        # Define price
        price = shareprice.price
        data.append({
            "time": time,
            "price": price
        })
    # Return results as JSON
    return jsonify(data)


@bp.route('/tasks/updateshares')
def sharesupdate():
    """
    Update shares database.

    """
    # Call database to get new share data
    gdb.updateshares()
    # Return a success response
    return jsonify(success=True)

@bp.route('/leaderboard', methods=['GET'])
@user_login_required
def leaderboard():
    """Displays overall leaderboard and top gainer leaderboards """
    
    leaderboard, current_user_info = gdb.getleaderboard(current_user.userID)

    weektopgainers, monthtopgainers = gdb.gettopgainers()

    # Render template
    return render_template('leaderboard.html', 
                            leaderboard=leaderboard,
                            current_user_info=current_user_info,
                            weektopgainers = weektopgainers,
                            monthtopgainers = monthtopgainers,
                            userbalance=current_user.balance)

@bp.route('/updateleaderboard')
def updateleaderboard():
    """
    Update leaderboard
    """
    gdb.updateleaderboard()

    return jsonify(success=True)