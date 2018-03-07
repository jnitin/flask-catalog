# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import ValidationError, HiddenField, BooleanField, StringField, \
                PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email
#ABfrom flask_wtf.html5 import EmailField
from wtforms.fields.html5 import EmailField

from application.user import User
from application.constants import AGREE_TIP


class LoginForm(FlaskForm):
    next = HiddenField()
    email = EmailField('Email',
                       [DataRequired(), Email()])
    password = PasswordField('Password',
                             [DataRequired()])
    remember = BooleanField('Remember me')
    # Use render_kw to set style of submit button
    submit = SubmitField('Log in',
                         render_kw={"class": "btn btn-success btn-block"})


class RegisterForm(FlaskForm):
    next = HiddenField()

    email = EmailField('Email',
                       [DataRequired(), Email()])
    password = PasswordField('Password',
                             [DataRequired()])
    name = StringField('Your Name',
                       [DataRequired()])
    # agree = BooleanField(AGREE_TIP, [DataRequired()])
    submit = SubmitField('Register',
                         render_kw={"class": "btn btn-success btn-block"})

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('This email is already registered')


class RecoverPasswordForm(FlaskForm):
    email = EmailField('Your email',
                       [DataRequired(),
                        Email()])
    submit = SubmitField('Send instructions')


class ChangePasswordForm(FlaskForm):
    activation_key = HiddenField()
    password = PasswordField('Password', [DataRequired()])
    password_again = PasswordField('Password again',
                                   [EqualTo('password',
                                            message="Passwords don't match")])
    submit = SubmitField('Save')


class ReauthForm(FlaskForm):
    next = HiddenField()
    password = PasswordField('Password',
                             [DataRequired()])
    submit = SubmitField('Reauthenticate')
