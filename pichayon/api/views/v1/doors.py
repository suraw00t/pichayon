from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, current_user

from pichayon.api import acl
from pichayon.api import schemas
from pichayon.api import models
from pichayon.api.renderers import render_json


module = Blueprint('api.v1.doors', __name__, url_prefix='/doors')


@module.route('', methods=['GET'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def list():
    schema = schemas.DoorSchema()
    doors = models.Door.objects()
    return render_json(schema.dump(doors, many=True))


@module.route('', methods=['POST'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def create():
    schema = schemas.DoorSchema()

    try:
        door_data = schema.load(request.get_json())
    except Exception as e:
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 400
        abort(response)

    user = current_user._get_current_object()
    door = models.Door(user=user,
                       **door_data)
    door.save()
    return render_json(schema.dump(door))


@module.route('/<door_id>', methods=['GET'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def get(door_id):
    door = None

    schema = schemas.DoorSchema()
    try:
        door = models.Door.objects.get(id=door_id)
    except Exception as e:
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 404
        abort(response)

    return render_json(schema.dump(door))


@module.route('/<door_id>', methods=['PUT'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def update(door_id):
    schema = schemas.DoorSchema()

    try:
        door = models.Door.objects.get(id=door_id)
        door_data = schema.load(request.get_json()).data

        door_data.pop('id')
        door.update(**door_data)
    except Exception as e:
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 400
        abort(response)

    door.save()
    return render_json(schema.dump(door))


@module.route('/<door_id>', methods=['DELETE'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def delete(door_id):
    door = None

    schema = schemas.DoorSchema()
    try:
        door = models.Door.objects.get(id=door_id)
    except Exception as e:
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 404
        abort(response)

    door.delete()

    return render_json(schema.dump(door))
