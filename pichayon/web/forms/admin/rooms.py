from wtforms import Form
from wtforms import fields
from wtforms import validators

from flask_wtf import FlaskForm

class RoomForm(FlaskForm):
    name = fields.StringField('Name',
                            validators=[validators.InputRequired(),
                                        validators.Length(min=3)])
    description = fields.StringField('Description')
