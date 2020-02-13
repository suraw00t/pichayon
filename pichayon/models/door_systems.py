import mongoengine as me

import datetime


class SparkbitDoorSystem(me.Document):
    door = me.ReferenceField('Door')

    name = me.StringField()
    host = me.StringField()

    created_date = me.DateTimeField(
            required=True,
            default=datetime.datetime.now)
    updated_date = me.DateTimeField(
            required=True,
            default=datetime.datetime.now)
