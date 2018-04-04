from flask_wtf import FlaskForm

from wtforms.fields.html5 import URLField, EmailField, TelField

from wtforms import ValidationError, StringField, PasswordField, SubmitField, \
    TextAreaField, FileField, DateField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, URL, \
    AnyOf, Optional
from flask_login import current_user


class AddCategoryForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    submit = SubmitField('Create')


class AddItemForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    description = TextAreaField('Description', [DataRequired()])
    submit = SubmitField('Create')