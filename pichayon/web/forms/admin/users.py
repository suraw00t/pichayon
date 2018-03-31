from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms.fields import html5

from flask_wtf import FlaskForm

class UserForm(FlaskForm):
    username = fields.TextField(
            'Name',
            validators=[validators.InputRequired(),
                        validators.Length(min=3)])
   # group = fields.ListField(Text.Field())
    
