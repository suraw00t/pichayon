import mongoengine as me

import datetime

from . import users

class RoomResquest(me.Document):
    meta = {"collection": "request_forms"}

    users = me.ReferenceField(users.User, dbref=True)
    started_date = me.DateTimeField(required=True)
    ended_date = me.DateTimeField(required=True)
    room = me.StringField()
    purpose = me.StringField(required=True)
