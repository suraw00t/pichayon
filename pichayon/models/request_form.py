import mongoengine as me

import datetime

from . import users


class RequestForm(me.Document):
    users = me.ReferenceField(users.User)
    started_date = me.DateTimeField(required=True)
    ended_date = me.DateTimeField(required=True)
    room = me.StringField()
    purpose = me.StringField(required=True)
