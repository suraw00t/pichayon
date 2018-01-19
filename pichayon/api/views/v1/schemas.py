from flask import Blueprint
from apispec import APISpec 
from marshmallow import fields

from pichayon.api.renderers import render_json
from pichayon.api import schemas

module = Blueprint('schemas', __name__, url_prefix='/schemas')



@module.route('')
def all():
    schema_list = schemas.__all__

    spec = APISpec(
        title='Pichayon API',
        version='1.0.0',
        plugins=[
            'apispec.ext.flask',
            'apispec.ext.marshmallow',
        ],
    )

    for schema in schema_list:
        spec.definition(schema.Meta.type_, schema=schema)
    return render_json(spec.to_dict())
    # return render_json(all_schemas)
