from .users import User
# from .users import User, AuthCode
# from .oauth2 import OAuth2Token

__all__ = [User]

from flask_mongoengine import MongoEngine

db = MongoEngine()


def init_db(app):
    db.init_app(app)
