import mongoengine as me

import datetime

from . import users


class RoomRequest(me.Document):
    meta = {"collection": "request_forms"}

    user = me.ReferenceField("User", dbref=True)
    started_date = me.DateTimeField(required=True, default=datetime.datetime.now())
    ended_date = me.DateTimeField(required=True)
    room = me.ReferenceField("Room", dbref=True)
    purpose = me.StringField(required=True)
