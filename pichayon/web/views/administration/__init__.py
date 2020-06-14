from flask import Blueprint

from pichayon.web import acl

from . import doors
from . import users
from . import groups
from . import door_authorizations
from . import sparkbit_systems
from . import history_logs

module = Blueprint('administration', __name__, url_prefix='/administration')

views = [users,
         doors,
         groups,
         door_authorizations,
         history_logs,
         sparkbit_systems
         ]


@module.route('/')
@acl.admin_permission.require(http_exception=403)
def index():
    return 'admin'
