from .users import User
from .doors import Door
from .rooms import Room

__all__ = [User, Door, Room]

from flask_mongoengine import MongoEngine

db = MongoEngine()


def init_db(app):
    db.init_app(app)
