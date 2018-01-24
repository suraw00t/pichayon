from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, current_user

from pichayon.api import acl
from pichayon.api import schemas
from pichayon.api import models
from pichayon.api.renderers import render_json


module = Blueprint('api.v1.groups', __name__, url_prefix='/groups')


@module.route('', methods=['GET'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def list():
    schema = schemas.GroupSchema()
    groups = models.Group.objects()
    return render_json(schema.dump(groups, many=True).data)


@module.route('', methods=['POST'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def create():
    schema = schemas.GroupSchema()

    try:
        group_data = schema.load(request.get_json()).data
    except Exception as e:
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 400
        abort(response)

    user = current_user._get_current_object()
    group = models.Group(user=user,
                         **group_data)
    group.save()
    return render_json(schema.dump(group).data)


@module.route('/<group_id>', methods=['GET'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def get(group_id):
    group = None

    schema = schemas.GroupSchema()
    try:
        group = models.Group.objects.get(id=group_id)
    except Exception as e:
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 404
        abort(response)

    return render_json(schema.dump(group).data)


@module.route('/<group_id>', methods=['PUT'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def update(group_id):
    schema = schemas.GroupSchema()

    try:
        group = models.Group.objects.get(id=group_id)
        group_data = schema.load(request.get_json()).data

        group_data.pop('id')
        group.update(**group_data)
    except Exception as e:
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 400
        abort(response)

    group.save()
    return render_json(schema.dump(group).data)


@module.route('/<group_id>', methods=['DELETE'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def delete(group_id):
    group = None

    schema = schemas.GroupSchema()
    try:
        group = models.Group.objects.get(id=group_id)
    except Exception as e:
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 404
        abort(response)

    group.delete()

    return render_json(schema.dump(group).data)
