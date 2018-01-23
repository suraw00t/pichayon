
from pichayon.utils import views

from . import site
from . import accounts

from . import dashboard


def register_blueprint(app):
    blueprints = views.get_subblueprints([site,
                                          accounts,
                                          dashboard])
    
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
