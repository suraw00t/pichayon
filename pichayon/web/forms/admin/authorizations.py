from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms import widgets
import datetime
from flask_wtf import FlaskForm

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class AuthorityForm(FlaskForm):
    user_group = fields.SelectField("User Group")
    door_group = fields.SelectField("Door Group")
    started_date = fields.DateTimeField(
        "Start Date",
        format="%Y-%m-%d %H:%M",
        default=datetime.datetime.now(),
        widget=widgets.TextInput(),
    )
    expired_date = fields.DateTimeField(
        "Expire Date",
        format="%Y-%m-%d %H:%M",
        default=datetime.datetime.now(),
        widget=widgets.TextInput(),
    )
    days = fields.SelectMultipleField(
        "Select Days",
        choices=[(i, day) for i, day in enumerate(DAYS)],
        coerce=int,
    )
    start_time = fields.TimeField(
        "Start Time",
        format="%H:%M",
        widget=widgets.TextInput(),
        validators=[validators.Optional()],
    )
    end_time = fields.TimeField(
        "End Time",
        format="%H:%M",
        widget=widgets.TextInput(),
        validators=[validators.Optional()],
    )
