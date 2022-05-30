from .users import User, Identity
from .doors import Door
from .door_systems import SparkbitDoorSystem
from .oauth2 import OAuth2Token
from .groups import UserGroup, UserGroupMember, DoorGroup
from .authorizations import GroupAuthorization, Rrule
from .history_logs import HistoryLog
from .request_forms import RoomResquest

__all__ = [
    User,
    Identity,
    Door,
    OAuth2Token,
    UserGroup,
    UserGroupMember,
    DoorGroup,
    GroupAuthorization,
    # DoorGroupAuthorization,
    # UserGroupAuthorization,
    Rrule,
    HistoryLog,
    SparkbitDoorSystem,
]

from flask_mongoengine import MongoEngine

db = MongoEngine()


def init_db(app):
    db.init_app(app)


def init_mongoengine(settings):
    import mongoengine as me

    dbname = settings.get("MONGODB_DB")
    host = settings.get("MONGODB_HOST", "localhost")
    port = int(settings.get("MONGODB_PORT", "27017"))
    username = settings.get("MONGODB_USERNAME", "")
    password = settings.get("MONGODB_PASSWORD", "")

    me.connect(db=dbname, host=host, port=port, username=username, password=password)
