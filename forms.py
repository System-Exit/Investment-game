from flask import Flask
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField,
                     SelectField, IntegerField)
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import DataRequired, Length, Regexp


class UserLoginForm(FlaskForm):
    """
    Form for user registration

    """
    username = StringField('Username', validators=[
        DataRequired('Username is required')])
    password = PasswordField('Password', validators=[
        DataRequired('Password is required')])
    submit = SubmitField('Log In')


class UserRegistrationForm(FlaskForm):
    """
    Form for user registration

    """
    username = StringField('Username', validators=[
        DataRequired('Username is required'),
        Length(min=3, max=32,
               message=("Username must be between"
                        " 3 and 32 characters long"))
        ])
    password = PasswordField('Password', validators=[
        DataRequired('Password is required'),
        Length(min=8, max=64,
               message=("Password must be between"
                        " 8 and 64 characters long")),
        Regexp(regex="(?=.*[A-Z]).",
               message="Password must contain an upper case letter"),
        Regexp(regex="(?=.*[a-z]).",
               message="Password must contain a lower case letter"),
        Regexp(regex="(?=.*\d).",
               message="Password must contain a number")
        ])
    fname = StringField('First Name', validators=[
        DataRequired('First name is required')])
    lname = StringField('Last Name', validators=[
        DataRequired('Last name is required')])
    dob = DateField('Date of Birth', validators=[
        DataRequired('Date of birth is requred')])
    email = EmailField('Email', validators=[
        DataRequired('Valid email address is required')])
    gender = SelectField('Gender', choices=[
        ('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    submit = SubmitField('Register')


class BuyShareForm(FlaskForm):
    """
    Form for buying shares

    """
    buysharecode = StringField('Company Code', validators=[
        DataRequired('Company Code is required')])
    buyquantity = IntegerField('Quantity to Purchase', validators=[
        DataRequired('Quantity is required')])
    buysubmit = SubmitField('Purchase', validators=[DataRequired()])


class SellShareForm(FlaskForm):
    """
    Form for selling shares

    """
    sellsharecode = StringField('Company Code', validators=[
        DataRequired('Company Code is required')])
    sellquantity = IntegerField('Quantity to Sell', validators=[
        DataRequired('Quantity is required')])
    sellsubmit = SubmitField('Sell', validators=[DataRequired()])
