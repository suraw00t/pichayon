from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms import widgets

from flask_wtf import FlaskForm
import datetime


class DoorGroupForm(FlaskForm):
    name = fields.StringField(
        "Name", validators=[validators.InputRequired(), validators.Length(min=3)]
    )
    description = fields.StringField("Description")


class DoorGroupMemberForm(FlaskForm):
    doors = fields.SelectMultipleField("Doors")


class UserGroupForm(FlaskForm):
    name = fields.StringField(
        "Name", validators=[validators.InputRequired(), validators.Length(min=3)]
    )
    description = fields.StringField("Description")


class UserGroupMemberForm(FlaskForm):
    users = fields.SelectMultipleField(
        "Users",
        validators=[validators.InputRequired()],
    )

    role = fields.SelectField(
        "Role",
        validators=[validators.InputRequired()],
        default="member",
        choices=[("member", "Member"), ("admin", "Admin")],
    )

    started_date = fields.DateTimeField(
        "Started Date",
        format="%Y-%m-%d %H:%M",
        default=datetime.date.today(),
        widget=widgets.TextInput(),
    )
    expired_date = fields.DateTimeField(
        "Expired Date",
        format="%Y-%m-%d %H:%M",
        validators=[validators.Optional()],
        widget=widgets.TextInput(),
    )
