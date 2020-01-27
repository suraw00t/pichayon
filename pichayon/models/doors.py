import mongoengine as me
import datetime
from pichayon import models


class Door(me.Document):
    name = me.StringField(required=True)
    device_id = me.StringField(unique=True)
    description = me.StringField()
    camera_url = me.StringField(default='', required=True)

    creator = me.ReferenceField('User', dbref=True)

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now,
                                    auto_now=True)
    status = me.StringField(required=True, default='active')

    meta = {'collection': 'doors'}

    def get_door_auth(self):
        door_group = models.DoorGroup.objects()
        door_auth = None
        for group in door_group:
            if group.is_member(self):
                door_auth = models.DoorAuthorizations.objects(door_group=group).first()
                break
        if door_auth:
            return door_auth
        return

