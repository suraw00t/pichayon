import mongoengine as me
import datetime


class DoorAuthorizations(me.Document):
    user_group = me.ReferenceField('UserGroup', dbref=True, required=True)
    door_group = me.ReferenceField('DoorGroup', dbref=True, required=True)

    started_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)
    expired_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.now)

    status = me.StringField(required=True, default='active')

    meta = {'collection': 'door_authorizations'}
