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
    room = models.Room.objects()
    return render_template("/rooms/index.html", room=room)

@module.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = forms.rooms.Room()
    if not form.validate_on_submit():
        return render_template(
            "/rooms/room.html", form = form,
        )

    room = models.Room.objects()

    form.populate_obj(room)

    room.save()

    return redirect(url_for('rooms.index'))
    