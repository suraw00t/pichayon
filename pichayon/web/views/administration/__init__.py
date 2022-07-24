from flask import Blueprint

from pichayon.web import acl

module = Blueprint("administration", __name__, url_prefix="/administration")


@module.route("/")
@acl.role_required("admin")
def index():
    return "admin"
