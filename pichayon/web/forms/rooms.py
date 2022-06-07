from wtforms import Form, fields, validators
from pichayon import models

import datetime

from flask_wtf import FlaskForm
from flask_mongoengine.wtf import model_form

Room = model_form(
    models.Room,
    FlaskForm,
    exclude=[],
    field_args={
        "name": {"label": "Name"},
    },
)


class Room(FlaskForm):
    pass
