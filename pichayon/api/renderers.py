from flask import jsonify
from flask.json import JSONEncoder

import bson
import datetime

def init_json_encoder(app):
    app.json_encoder = PichayonJSONEncoder


class PichayonJSONEncoder(JSONEncoder):
    def default(self, obj):
        # print('json', obj)
        try:
            if isinstance(obj, bson.ObjectId):
                return str(obj)
            if isinstance(obj, datetime.datetime):
                return obj.timestamp()
            if isinstance(obj, datetime.timedelta):
                return obj.timestamp()
        except TypeError as e:
            print(e)
        return JSONEncoder.default(self, obj)


def render_json(*args, **kwargs):
    """Wrapper around jsonify that sets the Content-Type of the response to
    application/vnd.api+json.
    """
    response = jsonify(*args, **kwargs)
    response.mimetype = 'application/vnd.api+json'
    return response
