from flask import Blueprint
from flask_jwt_extended import jwt_required

from pichayon.web import acl


module = Blueprint('api.v1.rooms', __name__, url_prefix='/rooms')


@module.route('')
@jwt_required
@acl.allows.requires(acl.is_admin)
def index():
    return '{"rooms":""}'
