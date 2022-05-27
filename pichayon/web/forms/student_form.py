from wtforms import Form
from wtforms import fields
from wtforms import validators

import datetime

from flask_wtf import FlaskForm


class StudentForm(FlaskForm):
    semester = fields.SelectField("Semester", choices=[("1", "2", "3")])
    room = fields.StringField("Room")
    purpose = fields.StringField("Purpose")
    request_date = fields.DateTimeField(required=True, default=datetime.datetime.now)
