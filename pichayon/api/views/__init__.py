from pichayon.utils import views as uviews

from . import v1
from . import accounts

def register_blueprint(app):
    views = [accounts, v1]

    uviews.register_subblueprint(app, views)
    
    v1.init_api(app)

