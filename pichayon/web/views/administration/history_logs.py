from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

from flask_login import login_user, logout_user, login_required, current_user
from flask_allows import Or
from pichayon import models
from pichayon.web import acl

module = Blueprint('administration.history_logs',
                   __name__,
                   url_prefix='/logs')


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    actions = ['create', 'update']
    logs = models.HistoryLog.objects(action__in=actions).order_by('-id')
    return render_template('/administration/history_logs/index.html',
                           logs=logs)

@module.route('door_group_log/<door_group_id>')
@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
def door_group_logs(door_group_id):
    door_group = models.DoorGroup.objects(id=door_group_id).first()
    selected_door = door_group.get_all_door_id()
    logs = models.HistoryLog.objects(action='open', details__door__in=selected_door).order_by('-id')
    

    return render_template('/administration/history_logs/index.html',
                           logs=logs,
                           door_group=door_group)