"""Define the forms of the catalog blueprint. (front-end)"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class AddCategoryForm(FlaskForm):
    """Form to add a category"""
    name = StringField('Name', [DataRequired()])
    submit = SubmitField('Create')


class EditCategoryForm(FlaskForm):
    """Form to edit a category"""
    name = StringField('Name', [DataRequired()])
    submit = SubmitField('Update')


class AddItemForm(FlaskForm):
    """Form to add an item"""
    name = StringField('Name', [DataRequired()])
    description = TextAreaField('Description', [DataRequired()])
    submit = SubmitField('Create')


class EditItemForm(FlaskForm):
    """Form to edit an item"""
    name = StringField('Name', [DataRequired()])
    description = TextAreaField('Description', [DataRequired()])
    submit = SubmitField('Update')
