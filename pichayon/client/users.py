from .common import base
# from . import roles


class User(base.Resource):
    __resource_name__ = 'users'
    # @property
    # def roles(self):
    #     user_roles = [roles.Role(self.manager.api.roles, r)
    #                   for r in self._info['roles']]
    #     return user_roles


class UserManager(base.Manager):
    __resource_class__ = User
    __resource_url__ = '/users'

    def create(self, **kwargs):
        user = self.__resource_class__(**kwargs)
        return self._create(user)

    def get(self, user_id):
        return self._get(user_id)
