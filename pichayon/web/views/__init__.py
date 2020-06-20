import datetime

from . import site
from . import accounts

from . import dashboard
from . import administration

views = [accounts,
         site,
         dashboard,
         administration,
         ]


def add_date_url(url):
    now = datetime.datetime.now()
    return f'{url}?date={now.strftime("%Y%m%d")}'


def get_subblueprints(views=[]):
    blueprints = []
    for view in views:
        blueprints.append(view.module)

        if 'views' in dir(view):
            for module in get_subblueprints(view.views):
                if view.module.url_prefix and module.url_prefix:
                    module.url_prefix = view.module.url_prefix + \
                            module.url_prefix
                blueprints.append(module)

    return blueprints


def register_blueprint(app):
    app.add_template_filter(add_date_url)

    blueprints = get_subblueprints(views)

    for blueprint in blueprints:
        app.register_blueprint(blueprint)
