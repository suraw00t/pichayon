from flask import Blueprint

from pichayon.web import acl

from . import doors
from . import rooms
from . import users

module = Blueprint('admin', __name__, url_prefix='/admin')

views = [users, doors, rooms]


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    return 'admin'
