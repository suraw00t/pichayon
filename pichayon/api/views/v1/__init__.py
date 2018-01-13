from flask import Blueprint
from apispec import APISpec

from . import rooms

module = Blueprint('api.v1', __name__, url_prefix='/v1')

subviews = [rooms]


from flask import Flask, jsonify
from marshmallow import Schema, fields
spec = APISpec(
    title='Swagger Petstore',
    version='1.0.0',
    plugins=[
        'apispec.ext.flask',
        'apispec.ext.marshmallow',
    ],
)

# Optional marshmallow support
class CategorySchema(Schema):
    id = fields.Int()
    name = fields.Str(required=True)

class PetSchema(Schema):
    category = fields.Nested(CategorySchema, many=True)
    name = fields.Str()


@module.route('/random')
def random_pet():
    """A cute furry animal endpoint.
    ---
    get:
        description: Get a random pet
        responses:
            200:
                description: A pet to be returned
                schema: PetSchema
    """
    pet = get_random_pet()
    return jsonify(PetSchema().dump(pet).data)

# Register entities and paths
spec.definition('Category', schema=CategorySchema)
spec.definition('Pet', schema=PetSchema)


def init_api(app):
    # with app.test_request_context():
    #     spec.add_path(view=random_pet)
    #     spec.add_path(view=random_pet)
    pass


@module.route('')
def index():
    return spec.to_dict()
