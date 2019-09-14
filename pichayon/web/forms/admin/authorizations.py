from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms.fields import html5

from flask_wtf import FlaskForm


class AddAuthorityForm(FlaskForm):
    user_group = fields.SelectMultipleField('User Group')
