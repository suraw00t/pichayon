from ..common import base
# from . import roles


class Group(base.Resource):
    __resource_name__ = 'groups'


class GroupManager(base.Manager):
    __resource_class__ = Group
    __resource_url__ = '/groups'
