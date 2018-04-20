"""Define the forms of the user blueprint. (front-end)"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import ValidationError, StringField, SubmitField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email
from flask_login import current_user
from ..extensions import images
from . import User


class ProfileForm(FlaskForm):
    """Form to update a user profile"""
    profile_pic = FileField('Profile Picture',
                            validators=[FileAllowed(images, 'Images only!')])
    email = EmailField('Email',
                       [DataRequired(), Email()])
    first_name = StringField('First Name',
                             [DataRequired()])
    last_name = StringField('Last Name',
                            [DataRequired()])
    submit = SubmitField('Update profile')

    def validate_email(self, field):
        """Check if email provided is already registered"""
        # pylint: disable=no-self-use

        email_current = current_user.email
        email_new = field.data
        if email_new != email_current:
            if User.query.filter_by(email=email_new).first() is not None:
                raise ValidationError('This email is already registered')
