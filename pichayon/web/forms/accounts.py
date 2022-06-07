from wtforms import Form
from wtforms import fields
from wtforms import validators

from flask_wtf import FlaskForm


class AccountForm(FlaskForm):
    first_name = fields.StringField(
        "First Name", validators=[validators.InputRequired(), validators.Length(min=3)]
    )
    last_name = fields.StringField(
        "Last Name", validators=[validators.InputRequired(), validators.Length(min=3)]
    )
    first_name_th = fields.StringField(
        "First Name (Thai)",
        validators=[validators.InputRequired(), validators.Length(min=3)],
    )
    last_name_th = fields.StringField(
        "Last Name (Thai)",
        validators=[validators.InputRequired(), validators.Length(min=3)],
    )
    id_card_number = fields.StringField(
        "ID Card Number",
        validators=[validators.InputRequired(), validators.Length(min=3)],
    )
