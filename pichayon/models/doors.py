import mongoengine as me
import datetime
from pichayon import models


class Door(me.Document):
    name = me.StringField(required=True, max_length=250)
    device_id = me.StringField(unique=True, max_length=250)
    description = me.StringField()
    camera_url = me.StringField(default='', required=True)
    # passcode = me.StringField(default='')
    groups = me.ListField(me.ReferenceField('DoorGroup'))

    creator = me.ReferenceField('User', dbref=True)
    have_web_open = me.BooleanField(default=False, required=True)
    have_passcode = me.BooleanField(default=False, required=True)
    
    status = me.StringField(required=True, default='active')
    type = me.StringField(required=True, default='pichayon')

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now,
                                    auto_now=True)


    meta = {'collection': 'doors'}
    
    def get_door_auth(self):
        door_group = models.DoorGroup.objects()
        door_auth = None
        for group in door_group:
            if group.is_member(self):
                door_auth = models.DoorAuthorization.objects(door_group=group).first()
                break
        if door_auth:
            return door_auth
        return

    def get_door_attributes(self):
        if type == 'sparkbit':
            return models.SparkbitDoorSystem.object.get(door=self)

        return None

