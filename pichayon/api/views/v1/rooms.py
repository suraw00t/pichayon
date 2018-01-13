from flask import Blueprint


module = Blueprint('api.v1.rooms', __name__, url_prefix='/rooms')


@module.route('')
def index():
    return '{"rooms":""}'
