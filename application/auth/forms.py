from flask_wtf import FlaskForm
from wtforms import ValidationError, HiddenField, BooleanField, StringField, \
                PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email
from wtforms.fields.html5 import EmailField
from flask_login import current_user

from ..user import User


class login_form(FlaskForm):
    email = EmailField('Email',
                       [DataRequired(), Email()])
    password = PasswordField('Password',
                             [DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')


class register_form(FlaskForm):
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
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('This email is already registered')


class register_invitation_form(FlaskForm):
    password = PasswordField('Password',
                             [DataRequired()])
    first_name = StringField('First Name',
                       [DataRequired()])
    last_name = StringField('Last Name',
                       [DataRequired()])
    submit = SubmitField('Register')
