from .users import User
from .doors import Door
from .rooms import Room
from .authorizations import Authorization

__all__ = [User, Door, Room, Authorization]

from flask_mongoengine import MongoEngine

db = MongoEngine()


def init_db(app):
    db.init_app(app)
