from flask_wtf import FlaskForm
from wtforms import ValidationError, BooleanField, StringField, \
                PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from wtforms.fields.html5 import EmailField

from ..user import User


class LoginForm(FlaskForm):
    email = EmailField('Email',
                       [DataRequired(), Email()])
    password = PasswordField('Password',
                             [DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')


class RegisterForm(FlaskForm):
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
        # pylint: disable=no-self-use
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('This email is already registered')


class RegisterInvitationForm(FlaskForm):
    password = PasswordField('Password',
                             [DataRequired()])
    first_name = StringField('First Name',
                             [DataRequired()])
    last_name = StringField('Last Name',
                            [DataRequired()])
    submit = SubmitField('Register')


class ResetPasswordRequestForm(FlaskForm):
    email = EmailField('Email',
                       [DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                             [DataRequired()])
    submit = SubmitField('Reset Password')
