import mongoengine as me
import datetime

from .users import User


class Group(me.Document):
    name = me.StringField(required=True, unique=True)
    description = me.StringField()

    user = me.ReferenceField(User, dbref=True)

    created_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow)
    updated_date = me.DateTimeField(required=True,
                                    default=datetime.datetime.utcnow,
                                    auto_now=True)

    meta = {'collection': 'groups'}

