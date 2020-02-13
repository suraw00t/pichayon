from .users import User
from .doors import Door
from .door_systems import SparkbitDoorSystem
from .oauth2 import OAuth2Token
from .groups import UserGroup, UserMember, DoorGroup
from .door_authorizations import DoorAuthorizations, GroupMember, Rrule

__all__ = [User,
           Door,
           OAuth2Token,
           UserGroup,
           UserMember,
           DoorGroup,
           DoorAuthorizations,
           GroupMember,
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

