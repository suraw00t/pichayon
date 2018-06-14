from flask import Blueprint

from principal import acl

from . import doors
from . import rooms
from . import users

module = Blueprint('web.dashboard.admin', __name__, url_prefix='/admin')

subviews = [users, doors, rooms]


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    return 'admin'
