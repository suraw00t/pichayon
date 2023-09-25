from wtforms import fields, widgets

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
        "updater",
        "camera_url",
        "is_passcode",
        "status",
        "ipv4",
        "begin_access_time",
        "end_access_time",
    ],
    field_args={
        "name": {"label": "Name"},
        "description": {"label": "Description"},
        "device_id": {"label": "Device ID"},
        "device_type": {"label": "Device Type"},
    },
)


class DoorForm(BaseDoorForm):
    device_type = fields.SelectField("Device Type")
    is_web_open = fields.BooleanField("Allow web open", default=False)
    is_auto_relock = fields.BooleanField("Allow auto relock", default=True)
    allow_read_sector0 = fields.BooleanField("Allow read sector 0", default=True)
    begin_access_time = fields.TimeField(
        "Begin allow access time",
        format="%H:%M",
        widget=widgets.TextInput(),
    )
    end_access_time = fields.TimeField(
        "End allow access time",
        format="%H:%M",
        widget=widgets.TextInput(),
    )


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
