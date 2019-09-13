from .users import User
from .doors import Door
from .oauth2 import OAuth2Token
from .groups import UserGroup, UserMember, DoorGroup

__all__ = [User, Door, OAuth2Token, UserGroup, UserMember, DoorGroup]

from flask_mongoengine import MongoEngine

db = MongoEngine()


def init_db(app):
    db.init_app(app)
