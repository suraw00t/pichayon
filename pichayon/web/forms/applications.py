from wtforms import Form, fields, validators
from pichayon import models

import datetime

from flask_wtf import FlaskForm
from flask_mongoengine.wtf import model_form

BaseApplicationForm = model_form(
    models.Application,
    FlaskForm,
    exclude=["users","status","created_date"],
    field_args={
        "advisor": {"label": "Advisor"},
        "started_date": {"label": "Start Date", "format": "%Y-%m-%d %H:%M"},
        "ended_date": {"label": "End Date", "format": "%Y-%m-%d %H:%M"},
        "room": {"label": "Room", "label_modifier": lambda r: r.name},
        "purpose": {"label": "Purpose"},
        "remark": {"label": "Remark"},
    },
)


class ApplicationForm(BaseApplicationForm):
    pass


# class RequestForm(FlaskForm):
#     started_date = fields.DateTimeField()
#     ended_date = fields.DateTimeField()
#     room = fields.StringField("Room", validators=[validators.InputRequired()])
#     purpose = fields.StringField("Purpose", validators=[validators.InputRequired()])
