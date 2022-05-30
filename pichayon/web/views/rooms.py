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

module = Blueprint("rooms", __name__, url_prefix="/rooms")


@module.route("/")
@login_required
def index():
    requests = models.RoomRequest.objects
    return render_template("/rooms/index.html", requests=requests)