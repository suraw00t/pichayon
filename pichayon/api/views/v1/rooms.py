from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, current_user

from pichayon.api import acl
from pichayon.api import schemas
from pichayon.api import models
from pichayon.api.renderers import render_json


module = Blueprint('api.v1.rooms', __name__, url_prefix='/rooms')


@module.route('', methods=['GET'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def list():
    schema = schemas.RoomSchema()
    rooms = models.Room.objects()
    
    return render_json(schema.dump(rooms, many=True).data)


@module.route('', methods=['POST'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def create():
    schema = schemas.RoomSchema()

    try:
        room_data = schema.load(request.get_json()).data
    except Exception as e:
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 400
        abort(response)

    user = current_user._get_current_object()
    room = models.Room(user=user,
                       **room_data)
    room.save()
    return render_json(schema.dump(room).data)


@module.route('/<room_id>', methods=['GET'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def get(room_id):
    room = None

    schema = schemas.RoomSchema()
    try:
        room = models.Room.objects.get(id=room_id)
    except Exception as e:
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 404
        abort(response)

    return render_json(schema.dump(room).data)


@module.route('/<room_id>', methods=['PUT'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def update(room_id):
    schema = schemas.RoomSchema()

    try:
        room = models.Room.objects.get(id=room_id)
        room_data = schema.load(request.get_json()).data

        room_data.pop('id')
        room.update(**room_data)
    except Exception as e:
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 400
        abort(response)

    room.save()
    return render_json(schema.dump(room).data)


@module.route('/<room_id>', methods=['DELETE'])
@jwt_required
@acl.allows.requires(acl.is_admin)
def delete(room_id):
    room = None

    schema = schemas.RoomSchema()
    try:
        room = models.Room.objects.get(id=room_id)
    except Exception as e:
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 404
        abort(response)

    room.delete()
    return render_json(schema.dump(room).data)
