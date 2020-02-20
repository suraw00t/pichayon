from wtforms import Form
from wtforms import fields
from wtforms import validators
from wtforms.fields import html5

from flask_wtf import FlaskForm


class DoorForm(FlaskForm):
    name = fields.TextField('Name',
                            validators=[validators.InputRequired(),
                                        validators.Length(min=3)])
    device_id = fields.TextField('Device ID')
    type = fields.SelectField()
    description = fields.TextField('Description')
    camera_url = fields.TextField('Camera URL')
    have_passcode = fields.BooleanField('Passcode')
    have_web_open = fields.BooleanField('Open via web')
