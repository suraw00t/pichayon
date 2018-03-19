import marshmallow as ma
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from . import common

class UserSchema(Schema):

    id = fields.String()
    username = ma.fields.String(required=True,
                                validator=ma.validate.Length(min=3, max=20))
    email = fields.String(required=False)
    first_name = fields.String(title='first-name', required=True)
    last_name = fields.String(title='last-name', required=True)
    status = fields.String(requred=True, default='distactive')
    groups = fields.List(fields.String(default='-'))
    roles = fields.List(fields.String())

    class Meta:
        type_ = 'users'
        # strict=True
        inflect = common.dasherize
