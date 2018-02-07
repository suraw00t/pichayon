from flask import Blueprint

from principal import acl

from . import groups
from . import rooms
from . import users

module = Blueprint('web.dashboard.admin', __name__, url_prefix='/admin')

subviews = [users, groups, rooms]


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    return 'admin'
