from .users import User
from .groups import Group

__all__ = [User, Group]

from flask_mongoengine import MongoEngine

db = MongoEngine()


def init_db(app):
    db.init_app(app)
