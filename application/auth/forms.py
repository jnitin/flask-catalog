from flask_wtf import FlaskForm
from wtforms import ValidationError, HiddenField, BooleanField, StringField, \
                PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email
from wtforms.fields.html5 import EmailField
from flask_login import current_user

from ..user import User


class LoginForm(FlaskForm):
    next = HiddenField()
    email = EmailField('Email',
                       [DataRequired(), Email()])
    password = PasswordField('Password',
                             [DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')
    # Use render_kw to set style of submit button
    #submit = SubmitField('Log in',
    #                     render_kw={"class": "btn btn-success btn-block"})


class RegisterForm(FlaskForm):
    next = HiddenField()

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


class RegisterInvitationForm(FlaskForm):
    next = HiddenField()

    password = PasswordField('Password',
                             [DataRequired()])
    first_name = StringField('First Name',
                       [DataRequired()])
    last_name = StringField('Last Name',
                       [DataRequired()])
    submit = SubmitField('Register')

class PasswordForm(FlaskForm):
    password = PasswordField('Current password', [DataRequired()])
    new_password = PasswordField('New password',
                                 [DataRequired()])
    password_again = PasswordField('Repeat new password',
                                   [DataRequired(),
                                    EqualTo('new_password')])
    submit = SubmitField('Update password',
                         render_kw={"class": "btn btn-success"})

    def validate_password(self, field):
        user = User.query.filter_by(id=current_user.id).first()
        if not user.verify_password(field.data):
            raise ValidationError("Current password is wrong.")
