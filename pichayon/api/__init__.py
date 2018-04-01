from flask import Flask

from . import views
from . import acl
from . import models
from . import oauth2
from . import renderers
from .. import caches
from .. import crypto

def create_app():
    app = Flask(__name__)
    app.config.from_object('pichayon.api.default_settings')
    app.config.from_envvar('PICHAYON_API_SETTINGS', silent=True)

    models.init_db(app)
    acl.init_jwt(app)
    renderers.init_json_encoder(app)
    caches.init_cache(app)
    crypto.init_crypto(app)
    
    views.register_blueprint(app)

    return app
