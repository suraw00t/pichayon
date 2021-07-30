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

module = Blueprint('door_groups',
                   __name__,
                   url_prefix='/doors/groups')


@module.route('')
#@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
@acl.admin_permission.require(http_exception=403)
def index():
    door_groups = models.DoorGroup.objects(status='active').order_by('name')
    return render_template(
            '/administration/door_groups/index.html',
            door_groups=door_groups)


@module.route('/<door_group_id>')
@acl.role_required('admin')
def view(door_group_id):
    door_group = models.DoorGroup.objects.get(id=door_group_id)

    return render_template(
            '/administration/door_groups/view.html',
            door_group=door_group
            )

@module.route('/create', methods=["GET", "POST"])
#@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
@acl.admin_permission.require(http_exception=403)
def create():
    form = DoorGroupForm()
    if not form.validate_on_submit():
        return render_template('/administration/door_groups/create-edit.html',
                               form=form)
    door_group = models.DoorGroup()
    form.populate_obj(door_group)
    door_group.creator = current_user._get_current_object()
    door_group.save()
    door_auth = models.DoorAuthorization(door_group=door_group)
    logs = models.HistoryLog(
                action = 'create',
                message = f'{current_user._get_current_object().username} has created a door group: {door_group.name}',
                details = {
                    'user': current_user._get_current_object().username,
                    'door_group': door_group.name,
                    },
                recorded_date = datetime.datetime.now()
            )
    logs.save()
    door_auth.save()
    return redirect(url_for('door_groups.index'))


@module.route('/<door_group_id>/edit', methods=["GET", "POST"])
#@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
@acl.admin_permission.require(http_exception=403)
def edit(door_group_id):
    group = models.DoorGroup.objects.get(id=door_group_id)

    form = DoorGroupForm(obj=group)
    if not form.validate_on_submit():
        return render_template('/administration/door_groups/create-edit.html',
                               form=form)

    form.populate_obj(group)
    group.save()
    logs = models.HistoryLog(
                action = 'update',
                message = f'{current_user._get_current_object().username} has updated a door group: {group.name}',
                details = {
                    'user': current_user._get_current_object().username,
                    'door_group': group.name,
                    },
                recorded_date = datetime.datetime.now()
            )
    logs.save()

    return redirect(url_for('door_groups.index'))

@module.route('/<door_group_id>/delete')
#@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
@acl.admin_permission.require(http_exception=403)
def delete(door_group_id):
    group = models.DoorGroup.objects.get(id=door_group_id)
    # group.status = 'delete'
    door_auth = models.DoorAuthorization.objects.get(door_group=group)
    
    
    for door in door_auth.door_group.members:
            door.delete()
    door_auth.delete()
    group.delete()
    logs = models.HistoryLog(
                action = 'delete',
                message = f'{current_user._get_current_object().username} has deleted a door group: {group.name}',
                details = {
                    'user': current_user._get_current_object().username,
                    'door_group': group.name,
                    },
                recorded_date = datetime.datetime.now()
            )
    logs.save()

    return redirect(url_for('door_groups.index'))
