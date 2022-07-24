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
from pichayon.web import forms

module = Blueprint("applications", __name__, url_prefix="/applications")


@module.route("")
@acl.role_required("admin")
def index():
    user = current_user._get_current_object()
    applications = models.Application.objects()
    return render_template(
        "/administration/applications/index.html", applications=applications)


@module.route("/<application_id>/approve")
@acl.role_required("admin")
def approve(application_id):
    application = models.Application.objects().get(id=application_id)
    application.status = "Approved"
    application.save()

    return redirect(url_for("administration.applications.comment"))

@module.route("/<application_id>/reject")
@acl.role_required("admin")
def reject(application_id):
    application = models.Application.objects().get(id=application_id)
    application.status = "Rejected"
    application.save()

    return redirect(url_for("administration.applications.comment"))


@module.route("/applications/comments", methods=["GET", "POST"])
@acl.role_required("admin")
def comment():

    application = models.Application.objects()
    form = forms.applications.ApplicationForm()
    if not form.validate_on_submit():
        return render_template(
            "/administration/applications/comment.html",
            form=form,
        )

    application = models.Application()

    form.populate_obj(application)
    application.user = current_user._get_current_object()

    application.save()

    return redirect(url_for("administration.applications.index"))


