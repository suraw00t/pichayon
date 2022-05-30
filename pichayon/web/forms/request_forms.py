from wtforms import Form
from wtforms import fields
from wtforms import validators

import datetime

from flask_wtf import FlaskForm


class RequestForm(FlaskForm):
    started_date = fields.DateTimeField()
    ended_date = fields.DateTimeField()
    room = fields.StringField("Room")
    purpose = fields.StringField("Purpose")
    
