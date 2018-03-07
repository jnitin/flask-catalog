from flask_wtf import FlaskForm
#AB from flask_wtf.html5 import URLField, EmailField, TelField
from wtforms.fields.html5 import URLField, EmailField, TelField

from wtforms import ValidationError, StringField, PasswordField, SubmitField, \
    TextAreaField, FileField, DateField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, URL, \
    AnyOf, Optional
from flask_login import current_user

from application.user import User


class ProfileForm(FlaskForm):
    email = EmailField('Email', [DataRequired(), Email()])
    name = StringField('Name', [DataRequired()])
    submit = SubmitField('Update profile',
                         render_kw={"class": "btn btn-success"})

    def validate_email(form, field):
        user = User.query.filter_by(id=current_user.id).first()
        email_current = user.email
        email_new = field.data
        if email_new != email_current:
            if User.query.filter_by(email=email_new).first() is not None:
                raise ValidationError('This email is already registered')


class PasswordForm(FlaskForm):
    password = PasswordField('Current password', [DataRequired()])
    new_password = PasswordField('New password',
                                 [DataRequired()])
    password_again = PasswordField('Repeat new password',
                                   [DataRequired(),
                                    EqualTo('new_password')])
    submit = SubmitField('Update password',
                         render_kw={"class": "btn btn-success"})

    def validate_password(form, field):
        user = User.query.filter_by(id=current_user.id).first()
        if not user.verify_password(field.data):
            raise ValidationError("Current password is wrong.")
