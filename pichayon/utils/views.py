def get_subblueprints(views=[]):
    blueprints = []
    for view in views:
        blueprints.append(view.module)

        if "subviews" in dir(view):
            for module in get_subblueprints(view.subviews):
                if view.module.url_prefix and module.url_prefix:
                    module.url_prefix = view.module.url_prefix + module.url_prefix
                blueprints.append(module)

    return blueprints


def register_subblueprint(app, views):
    blueprints = get_subblueprints(views)

    for blueprint in blueprints:
        app.register_blueprint(blueprint)
