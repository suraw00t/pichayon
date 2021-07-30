from flask import Blueprint

from pichayon.web import acl

from . import doors
from . import users
from . import user_groups
from . import door_groups
from . import authorizations
from . import sparkbit_systems
from . import history_logs

module = Blueprint('administration', __name__, url_prefix='/administration')

views = [users,
         doors,
         door_groups,
         user_groups,
         authorizations,
         history_logs,
         sparkbit_systems
         ]


@module.route('/')
@acl.admin_permission.require(http_exception=403)
def index():
    return 'admin'
