from flask import Blueprint, render_template, redirect, url_for, g

from flask_login import login_user, logout_user, login_required, current_user
from pichayon import models
from pichayon.web import acl

module = Blueprint("history_logs", __name__, url_prefix="/logs")


@module.route("/")
# @acl.allows.requires(acl.is_admin)
# @acl.admin_permission.require(http_exception=403)
@acl.role_required("admin")
def index():
    remove_actions = ["door-status"]
    logs = (
        models.HistoryLog.objects(
            action__nin=remove_actions,
            # user__ne=None,
        )
        .limit(100)
        .order_by("-id")
    )
    # logs = models.HistoryLog.objects().order_by('-id').limit(100)
    return render_template("/administration/history_logs/index.html", logs=logs)


@module.route("doors/<door_id>")
# @acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
# @acl.admin_permission.require(http_exception=403)
@acl.role_required("admin")
def door_logs(door_id):
    remove_actions = ["door-status"]
    door = models.Door.objects(id=door_id).first()
    logs = (
        models.HistoryLog.objects(
            door=door,
            action__nin=remove_actions,
        )
        .limit(100)
        .order_by("-id")
    )

    return render_template(
        "/administration/history_logs/index.html", logs=logs, door=door
    )
