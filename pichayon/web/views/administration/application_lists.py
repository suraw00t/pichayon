import datetime

from flask import (
    Blueprint,
    current_app,
    render_template,
    url_for,
    redirect,
    request,
    session,
)

from flask_login import login_user, logout_user, login_required, current_user

from pichayon import models
from pichayon.web import acl
from pichayon.web.forms.admin import *
from flask_login import login_user, logout_user, login_required, current_user

module = Blueprint("application_lists", __name__, url_prefix="/application_lists")

@module.route("")
@acl.role_required("admin")
def index():
    user = current_user._get_current_object()
    app_lists = models.Application.objects()
    return render_template(
        "/administration/application_lists/index.html", app_lists=app_lists
    )


# @module.route("")
# @acl.role_required("admin")
# def show():

@module.route("/<app_lists_id/approve")
@acl.role_required("admin")
def approve(app_lists_id):
    app_lists = models.Application.objects().get(id=app_lists_id)
    app_lists = stat
    