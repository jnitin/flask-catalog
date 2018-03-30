from flask_wtf import FlaskForm

from wtforms.fields.html5 import URLField, EmailField, TelField

from wtforms import ValidationError, StringField, PasswordField, SubmitField, \
    TextAreaField, FileField, DateField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, URL, \
    AnyOf, Optional
from flask_login import current_user

from flask_wtf.file import FileAllowed, FileRequired
from ..extensions import images

from . import User


class ProfileForm(FlaskForm):
    email = EmailField('Email', [DataRequired(), Email()])
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])
    submit = SubmitField('Update profile')

    def validate_email(self, field):
        email_current = current_user.email
        email_new = field.data
        if email_new != email_current:
            if User.query.filter_by(email=email_new).first() is not None:
                raise ValidationError('This email is already registered')


class ProfilePicForm(FlaskForm):
    profile_pic = FileField('Profile Picture',
                            validators=[FileRequired(),
                                        FileAllowed(images, 'Images only!')])
    submit = SubmitField('Update profile picture')

