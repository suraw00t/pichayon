import mongoengine as me
import datetime


class Door(me.Document):
    name = me.StringField(required=True)
    device_id = me.StringField()
    description = me.StringField()


    creator = me.ReferenceField('User', dbref=True)

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now,
                                    auto_now=True)
    status = me.StringField(required=True, default='active')

    meta = {'collection': 'doors'}
