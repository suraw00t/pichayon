from flask import Blueprint
from apispec import APISpec

from . import schemas
from . import auth
from . import users
from . import rooms

module = Blueprint('api.v1', __name__, url_prefix='/v1')

subviews = [schemas,
            auth,
            users,
            rooms]
