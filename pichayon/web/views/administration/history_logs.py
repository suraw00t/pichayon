from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

from flask_login import login_user, logout_user, login_required, current_user
from pichayon import models
from pichayon.web import acl

module = Blueprint('history_logs',
                   __name__,
                   url_prefix='/logs')


@module.route('/')
#@acl.allows.requires(acl.is_admin)
@acl.admin_permission.require(http_exception=403)
def index():
    actions = ['create', 'update']
    logs = models.HistoryLog.objects(action__in=actions).order_by('-id')
    return render_template('/administration/history_logs/index.html',
                           logs=logs)

@module.route('doors/<door_id>')
#@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
# @acl.admin_permission.require(http_exception=403)
@acl.role_required('admin')
def door_logs(door_id):
    door = models.Door.objects(id=door_id).first()
    logs = models.HistoryLog.objects(door=door).order_by('-id').limit(100)
    

    return render_template('/administration/history_logs/index.html',
                           logs=logs,
                           door=door)
