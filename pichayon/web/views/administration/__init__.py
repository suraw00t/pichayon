from flask import Blueprint

from pichayon.web import acl

from . import doors
from . import users
from . import groups

module = Blueprint('administration', __name__, url_prefix='/administration')

views = [users,
         doors,
         groups
         ]


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    return 'admin'
