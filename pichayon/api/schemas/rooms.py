import marshmallow as ma
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from . import common

class RoomSchema(Schema):

    id = fields.String(dump_only=True)
    name = ma.fields.String(required=True,
                            validator=ma.validate.Length(min=3, max=20))
    status = fields.String(requred=True, default='disactive')

    class Meta:
        type_ = 'rooms'
        strict=True
        inflect = common.dasherize
