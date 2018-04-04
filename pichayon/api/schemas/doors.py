import marshmallow as ma
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from . import common


class DoorSchema(Schema):

    id = fields.String()
    name = ma.fields.String(required=True,
                            validator=ma.validate.Length(min=3))
    description = fields.String()
    created_date = fields.DateTime()
    updated_date = fields.DateTime()

    class Meta:
        type_ = 'doors'
        strict = True
        inflect = common.dasherize
