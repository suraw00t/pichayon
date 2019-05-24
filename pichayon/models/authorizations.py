import mongoengine as me
import datetime

from .users import User
from .rooms import Room


class Authorization(me.Document):
    user = me.ReferenceField(User, dbref=True)
    room = me.ReferenceField(Room, dbref=True)

    started_date = me.DateTimeField(default=datetime.datetime.utcnow())
    expires_date = me.DateTimeField(default=datetime.datetime.utcnow())

    grantor = me.ReferenceField(User, dbref=True)
    granted_date = me.DateTimeField(defaut=datetime.datetime.utcnow())

    other = me.DictField()
    
    meta = {'collection' : 'authorizations'}
