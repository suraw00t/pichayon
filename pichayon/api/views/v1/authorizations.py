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

module = Blueprint('api.v1.authorizations', __name__,
        url_prefix='/authorizations')


@module.route('', methods=['GET'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def list():
    schema = schemas.AuthorizationSchema()
    authorizations = models.Authorization.objects()

    return render_json(schema.dump(authorizations, many=True).data)


@module.route('', methods=['post'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def create():
    schema = schemas.AuthorizationSchema()
    try:
        print(request.get_json())
        auth_data = schema.load(request.get_json()).data
    except Exception as e:
        print(e)
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 400
        abort(response)


    print('got data:', auth_data)
    user = models.User.objects(id=auth_data['user']['id']).first()
    if not user:
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 400
        abort(response)

    room = models.Room.objects(id=auth_data['room']['id']).first()

    auth = models.Authorization(user=user,
                                room=room,
                                grantor=current_user._get_current_object(),
                                started_date=auth_data['started_date'],
                                expires_date=auth_data['expires_date'],
                                )
    auth.save()

    return render_json(schema.dump(auth).data)


# @module.route('/<user_id>', methods=['PUT'])
# @jwt_required
# @acl.allows.requires(acl.is_admin)
# def update(user_id):
#     schema = schemas.UserSchema()

#     try:
#         user = models.User.objects.get(id=user_id)
#         user_data = schema.load(request.get_json()).data

#         user_data.pop('id')
#         user.update(**user_data)
    
#     except Exception as e:
#         response_dict = request.get_json()
#         response_dict.update(e.messages)
#         response = render_json(response_dict)
#         response.status_code = 400
#         abort(response)

#     user.save()
#     return render_json(schema.dump(user).data)


# @module.route('/<user_id>', methods=['get'])
# @jwt_required
# def get(user_id):
#     user = current_user
#     schema = schemas.UserSchema()
#     if 'admin' in current_user.roles:
#         user = models.User.objects(id=user_id).first()
        
#     return render_json(schema.dump(user).data)

# # @module.route('/<user_id>', methode=['DELETE'])
# # @jwt_required
# # @acl.allows.requires(acl.is_admin)
# # def delete(user_id):
# #     user = None

# #     schema = schemas.UserSchema()

# #     try:
# #         user = models.USer.objects.get(id=room_id)
# #     except Exception as e:
# #         response_dict = request.get_json()
# #         response_dict.update(e.messages)
# #         response = render_json(response_dict)
# #         response.status_code = 404
# #         abort(response)

# #     user.delete()
# #     return render_json(schema.dump(user).data)
