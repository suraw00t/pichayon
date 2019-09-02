from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms.fields import html5

from flask_wtf import FlaskForm


class AccountForm(FlaskForm):
    first_name = fields.TextField('First Name',
                                  validators=[validators.InputRequired(),
                                  validators.Length(min=3)])
    last_name = fields.TextField('Last Name',
                                 validators=[validators.InputRequired(),
                                 validators.Length(min=3)])
    id_card_number = fields.TextField('ID Card Number',
                                 validators=[validators.InputRequired(),
                                 validators.Length(min=3)])
