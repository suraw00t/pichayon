import marshmallow as ma
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from . import common
from . import users
from . import rooms

class AuthorizationSchema(Schema):

    id = fields.String()
    user = fields.Relationship(
            related_url='/users/{user_id}',
            related_url_kwargs={'user_id':'<id>'},
            many=False,
            schema=users.UserSchema,
            include_resource_linkage=True,
            type_='users',
        # dump_only=True
            )

    room = fields.Relationship(
            related_url='/rooms/{room_id}',
            related_url_kwargs={'room_id':'<id>'},
            many=False,
            schema=rooms.RoomSchema,
            include_resource_linkage=True,
            type_='rooms',
        # dump_only=True
            )

    started_date = fields.DateTime()
    expires_date = fields.DateTime()

    grantor = fields.Relationship(
            related_url='/users/{user_id}',
            related_url_kwargs={'user_id':'<id>'},
            many=False,
            schema=users.UserSchema,
            include_resource_linkage=True,
            type_='users',
            dump_only=True
            )

    granted_date = fields.DateTime(dump_only=True)

    class Meta:
        type_ = 'authorizations'
        strict = True
        inflect = common.dasherize
