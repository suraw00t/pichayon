from wtforms import Form, fields, validators
from pichayon import models

import datetime

from flask_wtf import FlaskForm
from flask_mongoengine.wtf import model_form

RequestForm = model_form(
    models.RoomRequest,
    FlaskForm,
    exclude=["users"],
    field_args={
        "users": {"label": "Users"},
        "started_date": {"label": "Started"},
        "ended_date": {"label": "Ended"},
        "room": {"label": "Room"},
        "purpose": {"label": "Purpose"},
    },
)


class RequestForm(RequestForm):
    pass


# class RequestForm(FlaskForm):
#     started_date = fields.DateTimeField()
#     ended_date = fields.DateTimeField()
#     room = fields.StringField("Room", validators=[validators.InputRequired()])
#     purpose = fields.StringField("Purpose", validators=[validators.InputRequired()])
