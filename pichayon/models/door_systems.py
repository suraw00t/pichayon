import mongoengine as me

import datetime


class SparkbitDoorSystem(me.Document):
    door = me.ReferenceField('Door')

    name = me.StringField(required=True)
    description = me.StringField()

    device_id = me.StringField(required=True)
    creator = me.ReferenceField('User', required=True)

    status = me.StringField(default='active')

    created_date = me.DateTimeField(
            required=True,
            default=datetime.datetime.now)
    updated_date = me.DateTimeField(
            required=True,
            default=datetime.datetime.now,
            auto_now=True)
