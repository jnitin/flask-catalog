"""Define the forms of the auth blueprint. (front-end)"""
from flask_wtf import FlaskForm
from wtforms import ValidationError, BooleanField, StringField, \
                PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from wtforms.fields.html5 import EmailField

from ..user import User


class LoginForm(FlaskForm):
    """Form to authenticate a user to login"""
    email = EmailField('Email',
                       [DataRequired(), Email()])
    password = PasswordField('Password',
                             [DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')


class RegisterForm(FlaskForm):
    """Form to allow a user to register"""
    email = EmailField('Email',
                       [DataRequired(), Email()])
    password = PasswordField('Password',
                             [DataRequired()])
    first_name = StringField('First Name',
                             [DataRequired()])
    last_name = StringField('Last Name',
                            [DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        """Check if email provided on the registration form already exists"""
        # pylint: disable=no-self-use
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('This email is already registered')


class RegisterInvitationForm(FlaskForm):
    """Form to allow an invited user to register"""
    password = PasswordField('Password',
                             [DataRequired()])
    first_name = StringField('First Name',
                             [DataRequired()])
    last_name = StringField('Last Name',
                            [DataRequired()])
    submit = SubmitField('Register')


class ResetPasswordRequestForm(FlaskForm):
    """Form to allow a user to request a reset password email"""
    email = EmailField('Email',
                       [DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    """Form to allow a user to reset password"""
    password = PasswordField('Password',
                             [DataRequired()])
    submit = SubmitField('Reset Password')
