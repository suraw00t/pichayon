from wtforms import Form, fields, validators
from pichayon import models

import datetime

from flask_wtf import FlaskForm
from flask_mongoengine.wtf import model_form

BaseApplicationForm = model_form(
    models.Application,
    FlaskForm,
    exclude=["users", "status", "created_date"],
    field_args={
        "degree": {"label": "Degrees"},
        "advisor": {
            "label": "Advisor",
            "label_modifier": lambda ad: f"{ad.first_name} {ad.last_name}",
        },
        "started_date": {"label": "Start Date", "format": "%Y-%m-%d %H:%M"},
        "ended_date": {"label": "End Date", "format": "%Y-%m-%d %H:%M"},
        "room": {"label": "Room", "label_modifier": lambda r: r.name},
        "purpose": {"label": "Purpose"},
        "remark": {"label": "Remark"},
    },
)


class ApplicationForm(BaseApplicationForm):
    pass
