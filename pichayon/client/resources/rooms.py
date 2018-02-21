from ..common import base
# from . import roles


class Room(base.Resource):
    __resource_name__ = 'rooms'


class RoomManager(base.Manager):
    __resource_class__ = Room
    __resource_url__ = '/rooms'
