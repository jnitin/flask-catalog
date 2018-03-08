from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField


class ItemsForm(FlaskForm):
    name = StringField('TO REPLACE WITH A LIST, NOT A FORM...')
    submit = SubmitField('TO REPLACE WITH NON-FORM',
                         render_kw={"class": "btn btn-success"})
