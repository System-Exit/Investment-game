from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class UserLoginForm(FlaskForm):
    """
    Form for user registration

    """
    username = StringField('Username', validators=[DataRequired('Username is required')])
    password = PasswordField('Password', validators=[DataRequired('Password is required')])
    submit = SubmitField('Log In')