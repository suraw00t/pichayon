from ..common import base
# from . import roles


class Door(base.Resource):
    __resource_name__ = 'doors'


class DoorManager(base.Manager):
    __resource_class__ = Door
    __resource_url__ = '/doors'
