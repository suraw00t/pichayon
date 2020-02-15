from .users import User
from .doors import Door
from .door_systems import SparkbitDoorSystem
from .oauth2 import OAuth2Token
from .groups import UserGroup, UserGroupMember, DoorGroup
from .door_authorizations import DoorAuthorization, AuthorizationGroup, Rrule

__all__ = [User,
           Door,
           OAuth2Token,
           UserGroup,
           UserGroupMember,
           DoorGroup,
           DoorAuthorization,
           AuthorizationGroup,
           Rrule,
           SparkbitDoorSystem
           ]

from flask_mongoengine import MongoEngine

db = MongoEngine()


def init_db(app):
    db.init_app(app)


def init_mongoengine(settings):
    import mongoengine as me
    dbname = settings.get('MONGODB_DB')
    host = settings.get('MONGODB_HOST', 'localhost')
    port = int(settings.get('MONGODB_PORT', '27017'))
    username = settings.get('MONGODB_USERNAME', '')
    password = settings.get('MONGODB_PASSWORD', '')

    me.connect(db=dbname,
               host=host,
               port=port,
               username=username,
               password=password)

