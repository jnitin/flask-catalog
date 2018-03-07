# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
#AB from flask_wtf.html5 import URLField, EmailField, TelField
from wtforms.fields.html5 import URLField, EmailField, TelField

from wtforms import ValidationError, StringField, PasswordField, SubmitField, \
    TextAreaField, FileField, DateField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, URL, \
    AnyOf, Optional
from flask_login import current_user

from application.user import User
from application.constants import SEX_TYPES, \
    BIO_TIP, ALLOWED_AVATAR_EXTENSIONS
from application.utils import allowed_file


class ProfileForm(FlaskForm):
    email = EmailField('Email', [DataRequired(), Email()])
    name = StringField('Name', [DataRequired()])
    # avatar_file = FileField("Avatar", [Optional()])
    # phone = TelField('Phone', [DataRequired(), Length(max=64)])
    # url = URLField('URL', [Optional(), URL()])
    # location = StringField('Location', [Optional(), Length(max=64)])
    # bio = TextAreaField('Bio', [Optional(), Length(max=1024)],
    #                     description=BIO_TIP)
    submit = SubmitField('Update profile',
                         render_kw={"class": "btn btn-success"})

    def validate_email(form, field):
        user = User.query.filter_by(id=current_user.id).first()
        email_current = user.email
        email_new = field.data
        if email_new != email_current:
            if User.query.filter_by(email=email_new).first() is not None:
                raise ValidationError('This email is already registered')

    #def validate_avatar_file(form, field):
        #if field.data and not allowed_file(field.data.filename):
            #raise ValidationError("Please upload files with extensions: {}".format(
                                  #"/".join(ALLOWED_AVATAR_EXTENSIONS)))


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
