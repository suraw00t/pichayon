from flask import Flask

from . import views
from . import acl
from . import models
from . import oauth2
from . import renderers

def create_app():
    app = Flask(__name__)
    app.config.from_object('pichayon.api.default_settings')
    app.config.from_envvar('PICHAYON_API_SETTINGS', silent=True)

    models.init_db(app)
    acl.init_jwt(app)
    renderers.init_json_encoder(app)
    
    views.register_blueprint(app)

    return app
