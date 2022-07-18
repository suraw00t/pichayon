from flask import redirect, url_for, request
from flask_login import LoginManager, current_user, login_url
from werkzeug.exceptions import Forbidden
from functools import wraps


from .. import models


login_manager = LoginManager()


def init_acl(app):
    # initial login manager
    login_manager.init_app(app)

    @app.errorhandler(403)
    def page_not_found(e):
        return unauthorized_callback()


def role_required(*roles):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            for role in roles:
                if current_user.is_authenticated and role in current_user.roles:
                    return func(*args, **kwargs)
            raise Forbidden()

        return wrapped

    return wrapper


@login_manager.user_loader
def load_user(user_id):
    user = models.User.objects.with_id(user_id)
    return user


@login_manager.unauthorized_handler
def unauthorized_callback():
    print(request.method, request.url)
    if request.method == "GET":
        response = redirect(login_url("accounts.login", request.url))
        return response

    return redirect(url_for("accounts.login"))
