from ..common import base
# from . import roles


class Authorization(base.Resource):
    __resource_name__ = 'authorizations'


class AuthorizationManager(base.Manager):
    __resource_class__ = Authorization
    __resource_url__ = '/authorizations'
