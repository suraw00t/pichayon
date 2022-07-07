import mongoengine as me

import datetime

from . import users


class Application(me.Document):
    meta = {"collection": "applications"}

    user = me.ReferenceField("User", dbref=True)

    advisor = me.StringField(required=True)

    started_date = me.DateTimeField(required=True, default=datetime.datetime.now())
    ended_date = me.DateTimeField(required=True)

    room = me.ReferenceField("Door", dbref=True)
    purpose = me.StringField(required=True)
    status = me.StringField(required=True, default="Pending")
    remark = me.StringField()
