from .users import User
from .groups import Group
from .rooms import Room

__all__ = [User, Group, Room]

from flask_mongoengine import MongoEngine

db = MongoEngine()


def init_db(app):
    db.init_app(app)
