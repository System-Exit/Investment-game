from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SubmitField  

class Registration:
    pass

class UserRegistrationForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Next')
    fname = StringField('First Name')
    lname = StringField('Last Name')
    dob = DateField('Date of Birth')