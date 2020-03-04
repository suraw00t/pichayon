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
@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
def index():
    logs = models.HistoryLog.objects().order_by('-id')
    return render_template('/administration/history_logs/index.html',
                           logs=logs)

