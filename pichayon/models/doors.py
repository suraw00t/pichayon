import mongoengine as me
import datetime

from .users import User


class Door(me.Document):
    name = me.StringField(required=True, unique=True)
    description = me.StringField()

    creator = me.ReferenceField(User, dbref=True)

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow,
                                    auto_now=True)
    status = me.StringField(required=True, default='active')

    meta = {'collection': 'doors'}


class DoorAuthorization(me.Document):
    user = me.ReferenceField('User', dbref=True)
    door = me.ReferenceField('Door', dbref=True)
    grantor = me.ReferenceField('User', dbref=True)

    is_admin = me.BooleanField(required=True, default=False)
    started_date = me.DateTimeField(
            required=True,
            default=datetime.datetime.now)

    started_date = me.DateTimeField(
            required=True,
            default=datetime.datetime.now)

    ended_date = me.DateTimeField(
            required=True,
            default=datetime.datetime.now)

    granted_date = me.DateTimeField(
            required=True,
            default=datetime.datetime.now)
    updated_date = me.DateTimeField(
            required=True,
            default=datetime.datetime.utcnow,
            auto_now=True)

    meta = {'collection': 'door_authorizations'}
