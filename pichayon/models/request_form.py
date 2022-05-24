import mongoengine as me

import datetime

from . import users


class RequestForm(me.Document):
    users = me.ReferenceField(user.User)
    semester = me.IntField(required=True)
    room = me.StringField()
    purpose = me.StringField(required=True)
    tool = me.StringField()
    request_date = me.DateTimeField(required=True, default=datetime.datetime.now)
