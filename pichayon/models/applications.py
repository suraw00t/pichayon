import mongoengine as me

import datetime

from . import users


class Application(me.Document):
    meta = {"collection": "applications"}

    degrees = (
        ("ระดับปริญญาตรี", "Undergraduate Degrees"),
        ("ระดับปริญญาโท", "Graduate Degrees"),
    )

    user = me.ReferenceField("User", dbref=True)
    degree = me.StringField(choices=degrees)
    advisor = me.StringField(required=True)

    created_date = me.DateTimeField(default=datetime.datetime.now)
    started_date = me.DateTimeField(required=True, default=datetime.datetime.now())
    ended_date = me.DateTimeField(required=True)

    room = me.ReferenceField("Door", dbref=True)
    purpose = me.StringField(required=True)
    status = me.StringField(required=True, default="pending")
    remark = me.StringField()
    ip_address = me.StringField(max_length=255)
