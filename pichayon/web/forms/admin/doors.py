from wtforms import Form
from wtforms import fields
from wtforms import validators

from flask_wtf import FlaskForm
from flask_mongoengine.wtf import model_form
from pichayon import models

BaseDoorForm = model_form(
        models.Door,
        FlaskForm,
        exclude=[
            "created_date",
            "updated_date",
            "creator",
            "camera_url",
            "have_passcode",
            "have_web_open",
            'status',
            ],
        field_args={
            "name": {"label": "Name"},
            "description": {"label": "Description"},
            "device_id": {"label": "Device ID"},
            "type": {"label": "Type"},
        },

        )

class DoorForm(BaseDoorForm):
    type = fields.SelectField()



# class DoorForm(FlaskForm):
#     name = fields.StringField(
#             'Name',
#             validators=[validators.InputRequired(),
#                         validators.Length(min=3)])
#     description = fields.StringField('Description')

#     device_id = fields.StringField('Device ID')
#     type = fields.SelectField()

    
#     camera_url = fields.StringField('Camera URL')
#     have_passcode = fields.BooleanField('Passcode')
#     have_web_open = fields.BooleanField('Open via web')
