import marshmallow as ma
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from . import common

class UserSchema(Schema):

    id = fields.String()
    username = ma.fields.String(required=True,
                                validator=ma.validate.Length(min=3, max=20))
    email = fields.String(required=True)
    first_name = fields.String(title='first-name', required=True)
    last_name = fields.String(title='last-name', required=True)
    status = fields.String(required=True, default='distactive')
    rooms = fields.List(fields.String())
    roles = fields.List(fields.String())

    class Meta:
        type_ = 'users'
        # strict=True
        inflect = common.dasherize
