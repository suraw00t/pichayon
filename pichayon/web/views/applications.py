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
from flask_principal import identity_changed, Identity, AnonymousIdentity
from pichayon import models
from .. import oauth2
from .. import forms
from .. import views

module = Blueprint("applications", __name__, url_prefix="/application")


@module.route("/")
@login_required
def index():
    user = current_user._get_current_object()
    applications = models.Application.objects(user=user)
    return render_template("/applications/index.html", applications=applications)


@module.route("/applications", methods=["GET", "POST"])
@login_required
def apply():
    form = forms.applications.ApplicationForm()
    if not form.validate_on_submit():
        return render_template(
            "/applications/request.html",
            form=form,
        )

    application = models.Application()

    form.populate_obj(application)
    application.user = current_user._get_current_object()

    application.save()

    return redirect(url_for("applications.index"))

# @module.route("/<application_id>/delete")
# @login_required
# def delete(application_id):
#     application = models.Application.objects().get(id=application_id)
#     application.delete()

#     return redirect(url_for("applications.index"))

@module.route("/<application_id>/cancel")
@login_required
def cancel(application_id):
    application = models.Application.objects().get(id=application_id)
    application.status = "Canceled"
    application.save()

    return redirect(url_for("applications.index"))
   
