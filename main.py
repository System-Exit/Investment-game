from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from config import Config
from registration import UserRegistrationForm
from login import UserLoginForm


# Load app with bootstrap
app = Flask(__name__)
app.config.from_object(Config)
Bootstrap(app)

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

# Run the app
if __name__ == '__main__':
    app.run(debug=False)