from flask import (Blueprint,
                   request,
                   abort,
                   current_app)
from flask_jwt_extended import jwt_required, current_user

from pichayon.api import acl
from pichayon.api.renderers import render_json
from pichayon.api import models
from pichayon.api import schemas
from pichayon.api import oauth2
from .. import accounts

module = Blueprint('api.v1.users', __name__, url_prefix='/users')


@module.route('', methods=['GET'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def list():
    schema = schemas.UserSchema()
    users = models.User.objects()

    return render_json(schema.dump(users, many=True).data)


@module.route('', methods=['post'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def create():
    schema = schemas.UserSchema()
    try:
        user_data = schema.load(request.get_json()).data
    except Exception as e:
        print(e)
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 400
        abort(response)

    user = models.User.objects(username=user_data['username']).first()
    if user:
        return render_json(schema.dump(user).data)

    token = current_app.cache.get('users.{}'.format(current_user.id))
    access_token = current_app.crypto.decrypt(token['access_token'])
    token['access_token'] = access_token

    client = oauth2.get_oauth2_client(token)
    result = client.principal.get('users/{}'.format(user_data['username']))

    data = result.json()
    user = accounts.add_principal_user(data)

    return render_json(schema.dump(user).data)


@module.route('/<user_id>', methods=['get'])
@jwt_required
def get(user_id):
    schema = schemas.UserSchema()
    return render_json(schema.dump(current_user).data)
