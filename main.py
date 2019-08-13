from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from config import Config
from registration import *


# Load app with bootstrap
app = Flask(__name__)
app.config.from_object(Config)
Bootstrap(app)

# Routing for each page
# TODO: Change where routing is handled
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registration')
def registration():
    form = registration.RegistrationUserCredentialsForm()
    error = None
    if(form.validate_on_submit()):
        return render_template('dashboard.html') 
    return render_template('registration.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=False)