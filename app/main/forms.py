from flask import Flask
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField,
                     SelectField, IntegerField)
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import DataRequired, Length, Regexp
from wtforms import ValidationError
from gdb_api import GoogleDatabaseAPI
from datetime import datetime, timedelta
from app import gdb


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
               message=("Username must be between 3 and 32 characters long"))
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
    bday = StringField('Day', validators=[
        DataRequired('Day of birth is requred')])
    bmonth = StringField('Month', validators=[
        DataRequired('Month of birth is requred')])
    byear = StringField('Year', validators=[
        DataRequired('Year of birth is requred')])
    email = EmailField('Email', validators=[
        DataRequired('Valid email address is required')
        ])
    gender = SelectField('Gender', choices=[
        ('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    submit = SubmitField('Register')

    def validate(self):
        # Do initial validations
        validation = super(UserRegistrationForm, self).validate()
        # Return false if validations fail
        if(validation is False):
            return False
        # Check if username is already used
        if(gdb.getuserbyusername(self.username.data) is not None):
            self.username.errors.append(
                "Username is already used by another account")
            validation = False
        # Check if email is already used
        if(gdb.getuserbyemail(self.email.data) is not None):
            self.email.errors.append(
                "Email is already used by another account")
            validation = False
        # Validate date of birth fields together
        dob = f"{self.byear.data}-{self.bmonth.data}-{self.bday.data}"
        try:
            # Validate that date of birth is a valid date
            date = datetime.strptime(dob, '%Y-%m-%d')
            # Validate date is less than 100 years old
            if(date < datetime(1900, 1, 1)):
                raise ValueError
        except ValueError:
            self.byear.errors.append("Date of birth is invalid")
            validation = False
        # Return the result of validation
        return validation


class BuyShareForm(FlaskForm):
    """
    Form for buying shares

    """
    buysharecode = StringField('Company Code', validators=[
        DataRequired('Company Code is required')])
    buyquantity = IntegerField('Quantity to Purchase', validators=[
        DataRequired('Quantity is required')])
    buysubmit = SubmitField('Purchase', validators=[DataRequired()])

    def validate(self):
        # Do initial validations
        validation = super(BuyShareForm, self).validate()
        # Return false if validations fail
        if(validation is False):
            return False
        # Check that quantity is not negative
        if(self.buyquantity is not None and self.buyquantity.data < 0):
            self.buyquantity.errors.append("Quantity cannot be nagative")
            validation = False
        return validation


class SellShareForm(FlaskForm):
    """
    Form for selling shares

    """
    sellsharecode = StringField('Company Code', validators=[
        DataRequired('Company Code is required')])
    sellquantity = IntegerField('Quantity to Sell', validators=[
        DataRequired('Quantity is required')])
    sellsubmit = SubmitField('Sell', validators=[DataRequired()])

    def validate(self):
        # Do initial validations
        validation = super(SellShareForm, self).validate()
        # Return false if validations fail
        if(validation is False):
            return False
        # Check that quantity is not negative
        if(self.sellquantity.data < 0):
            self.buyquantity.errors.append("Quantity cannot be nagative")
            validation = False
        return validation
