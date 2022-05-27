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

module = Blueprint("request_form", __name__, url_prefix="/request")


@module.route("/")
@login_required
def index():
    requests = models.RequestForm.objects
    return render_template("/request/index.html", requests=requests)
