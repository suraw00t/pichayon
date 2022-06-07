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

module = Blueprint("request", __name__, url_prefix="/request")


@module.route("/")
@login_required
def index():
    requests = models.RoomRequest.objects()
    users = models.User.objects()
    return render_template("/request/index.html", requests=requests)


@module.route("/requests", methods=["GET", "POST"])
@login_required
def request():
    form = forms.request_forms.RequestForm()
    if not form.validate_on_submit():
        return render_template(
            "/request/request.html",
            form=form,
        )

    request = models.RoomRequest.objects()

    form.populate_obj(request)
    request.user = current_user._get_current_object()

    request.save()

    return redirect(url_for("request.index"))
