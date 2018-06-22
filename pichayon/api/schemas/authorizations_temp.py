import marshmallow as ma
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from . import common

class AuthorizationSchema(Schema):
    id = fields.String()
    username = ma.fields.String(required=True,
                                validator=ma.validate.Length(min=3, max=20))
    rooms = fields.List(fields.String())
    
    class Meta:
        type_ = 'authorizations'

        inflect = common.dasherize
