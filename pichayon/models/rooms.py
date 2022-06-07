import mongoengine as me

import datetime

from . import users


class Room(me.Document):
    meta = {"collection": "rooms"}

    name = me.StringField(required=True)
