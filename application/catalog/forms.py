from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class AddCategoryForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    submit = SubmitField('Create')


class EditCategoryForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    submit = SubmitField('Update')


class AddItemForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    description = TextAreaField('Description', [DataRequired()])
    submit = SubmitField('Create')


class EditItemForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    description = TextAreaField('Description', [DataRequired()])
    submit = SubmitField('Update')
