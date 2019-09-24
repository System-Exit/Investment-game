from flask import (Flask, render_template, request, session,
                   redirect, url_for, flash, jsonify, abort)
from models import User
from functools import wraps
from app import gdb, login_manager
from app.admin import bp
from app.admin.forms import AdminLoginForm


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
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Landing and login page for administators.

    """
    # Initialise login form
    form = AdminLoginForm()
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
            return redirect(url_for('admin.dashboard'))
        else:
            flash("Invalid username or password.", category="error")
            return redirect(url_for('admin.login'))
    # Render template
    return render_template('admin/login.html', form=form)


@bp.route('/logout')
def logout():
    """
    Handles logout for admin.

    """
    # Remove session admin authentication
    session.pop('authenticated_admin', None)
    # Redirect to admin login
    return redirect(url_for('admin.login'))


@bp.route('/dashboard')
@admin_login_required
def dashboard():
    """
    Displays dashboard for administrator.

    """
    # Render template
    return render_template('admin/dashboard.html')


@bp.route('/userlist')
@admin_login_required
def userlist():
    """
    Lists all users for administrator.

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
    # Get users
    users, usercount = gdb.getusers(
        orderby=orderby,
        order=order,
        offset=offset,
        limit=limit)
    # Render template
    return render_template('admin/userlist.html',
                           users=users,
                           usercount=usercount,
                           countperpage=limit)


@bp.route('/user/<userID>')
@admin_login_required
def user(userID):
    """
    Displays details of a user for an administrator.

    """
    # Get user based on user ID
    user = gdb.getuserbyid(userID)
    # Render template
    return render_template('admin/user.html', user=user)


@bp.route('/user/<userID>/ban')
@admin_login_required
def banuser(userID):
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
    return redirect(request.referrer or url_for('admin.dashboard'))


@bp.route('/user/<userID>/unban')
@admin_login_required
def unbanuser(userID):
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
    return redirect(request.referrer or url_for('admin.dashboard'))


@bp.route('/statistics')
@admin_login_required
def statistics():
    """
    Lists statistics of userbase to admin.

    """
    # Get all user statistics
    userstatistics = gdb.getuserstatistics()

    # Render template with statistics
    return render_template('admin/statistics.html',
                           userstatistics=userstatistics)
