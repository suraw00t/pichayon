from flask import Blueprint, redirect, url_for

from pichayon.web import acl

module = Blueprint("administration", __name__, url_prefix="/administration")


@module.route("/")
@acl.role_required("admin")
def index():
    return redirect(url_for("dashboard.index"))
