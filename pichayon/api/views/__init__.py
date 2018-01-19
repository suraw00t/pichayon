from pichayon.utils import views as uviews

from . import v1

def register_blueprint(app):
    views = [v1]

    uviews.register_subblueprint(app, views)
