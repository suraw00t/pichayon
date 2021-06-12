from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

from flask_login import login_user, logout_user, login_required, current_user
from pichayon import models
from pichayon.web import acl
from pichayon.web.forms.admin import DoorGroupForm, UserGroupForm
import datetime

module = Blueprint('user_groups',
                   __name__,
                   url_prefix='/users/groups')


@module.route('/')
#@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
@acl.admin_permission.require(http_exception=403)
def index():
    groups = models.UserGroup.objects(status='active').order_by('name')
    return render_template('/administration/user_groups/index.html',
                           groups=groups)


@module.route('/create', methods=["GET", "POST"])
#@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
@acl.admin_permission.require(http_exception=403)
def create():
    form = UserGroupForm()
    if not form.validate_on_submit():
        return render_template('/administration/user_groups/create-edit.html',
                               form=form)
    user_group = models.UserGroup()
    form.populate_obj(user_group)
    logs = models.HistoryLog(
                action = 'create',
                message = f'{current_user._get_current_object().username} has created a user group: {user_group.name}',
                details = {
                    'user': current_user._get_current_object().username,
                    'user_group': user_group.name,
                    },
                recorded_date = datetime.datetime.now()
            )

    user_group.save()
    logs.save()
    return redirect(url_for('user_groups.index'))


@module.route('/<user_group_id>/edit', methods=["GET", "POST"])
#@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
@acl.admin_permission.require(http_exception=403)
def edit(user_group_id):
    group = models.UserGroup.objects.get(id=group_id)

    form = UserGroupForm(obj=group)
    if not form.validate_on_submit():
        return render_template('/administration/user_groups/create-edit.html',
                               form=form)

    form.populate_obj(group)
    logs = models.HistoryLog(
                action = 'update',
                message = f'{current_user._get_current_object().username} has updated a user group: {group.name}',
                details = {
                    'user': current_user._get_current_object().username,
                    'user_group': group.name,
                    },
                recorded_date = datetime.datetime.now()
            )
    group.save()
    logs.save()

    return redirect(url_for('user_groups.index'))


@module.route('/<user_group_id>/delete')
#@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
@acl.admin_permission.require(http_exception=403)
def delete(user_group_id):
    selected_group = models.UserGroup.objects.get(id=user_group_id)
    door_auths = models.DoorAuthorization.objects()
    for door_auth in door_auths:
        door_auth.remove_member(selected_group)
    # group.status = 'delete'
    selected_group.delete()
    logs = models.HistoryLog(
                action = 'delete',
                message = f'{current_user._get_current_object().username} has deleted a user group: {selected_group.name}',
                details = {
                    'user': current_user._get_current_object().username,
                    'user_group': selected_group.name,
                    },
                recorded_date = datetime.datetime.now()
            )
    logs.save()

    return redirect(url_for('user_groups.index'))


