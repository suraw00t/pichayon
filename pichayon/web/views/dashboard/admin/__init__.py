from flask import Blueprint

from principal import acl

from . import groups

module = Blueprint('web.dashboard.admin', __name__, url_prefix='/admin')

subviews = [groups]

@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    return 'admin'
