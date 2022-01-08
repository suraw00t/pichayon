from flask import Blueprint

from pichayon.web import acl

module = Blueprint("administration", __name__, url_prefix="/administration")


@module.route("/")
@acl.admin_permission.require(http_exception=403)
def index():
    return "admin"
