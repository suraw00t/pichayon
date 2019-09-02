from .users import User
from .doors import Door, DoorAuthorization
from .oauth2 import OAuth2Token
from .groups import Group, GroupMember

__all__ = [User, Door, OAuth2Token, Group, GroupMember]

from flask_mongoengine import MongoEngine

db = MongoEngine()


def init_db(app):
    db.init_app(app)
