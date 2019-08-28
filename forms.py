from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import DataRequired


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
        DataRequired('Username is required')])
    password = PasswordField('Password', validators=[
        DataRequired('Password is required')])
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
    sharecode = StringField('Company Code', validators=[
        DataRequired('Company Code is required')]) 
    quantity = IntegerField('Quantity to Purchase', validators=[
        DataRequired('Quantity is required')])
    submit = SubmitField('Purchase')

      