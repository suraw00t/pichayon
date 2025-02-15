import mongoengine as me

import datetime

from . import users


class Application(me.Document):
    meta = {"collection": "applications"}

    degrees = (
        ("B.Eng. (CoE)", "B.Eng. (CoE)"),
        ("B.Eng. (AIE)", "B.Eng. (AIE)"),
        ("graduate", "Graduate Degrees"),
    )

    user = me.ReferenceField("User", dbref=True)
    degree = me.StringField(choices=degrees)
    advisor = me.ReferenceField("User", dbref=True)

    created_date = me.DateTimeField(default=datetime.datetime.now)
    started_date = me.DateTimeField(required=True, default=datetime.date.today)
    ended_date = me.DateTimeField(required=True)

    approved_by = me.ReferenceField("User", dbref=True)
    approved_date = me.DateTimeField()

    room = me.ReferenceField("Door", dbref=True)
    purpose = me.StringField(required=True)
    status = me.StringField(required=True, default="pending")
    remark = me.StringField()
    ip_address = me.StringField(max_length=255)

    request_checkbox = me.BooleanField(required=True, default=False)

    def get_user_group_members(self):
        from .groups import UserGroupMember

        return UserGroupMember.objects(application=self)
