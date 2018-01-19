from .common import base
# from . import roles


class Room(base.Resource):
    __resource_name__ = 'rooms'
    # @property
    # def roles(self):
    #     user_roles = [roles.Role(self.manager.api.roles, r)
    #                   for r in self._info['roles']]
    #     return user_roles


class RoomManager(base.Manager):
    __resource_class__ = Room
    __resource_url__ = '/rooms'

    def create(self, **kwargs):
        room = self.__resource_class__(**kwargs)
        return self._create(room)

    def get(self, room_id):
        return self._get(room_id)
