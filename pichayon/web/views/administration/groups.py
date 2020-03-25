from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

from flask_login import login_user, logout_user, login_required, current_user
from flask_allows import Or
from pichayon import models
from pichayon.web import acl
from pichayon.web.forms.admin import DoorGroupForm, UserGroupForm
import datetime

module = Blueprint('administration.groups',
                   __name__,
                   url_prefix='/groups')


@module.route('/')
@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
def index():
    groups = models.UserGroup.objects(status='active').order_by('name')
    return render_template('/administration/groups/index.html',
                           groups=groups)


@module.route('/create_usergroup', methods=["GET", "POST"])
@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
def create_usergroup():
    form = UserGroupForm()
    if not form.validate_on_submit():
        return render_template('/administration/groups/create-edit.html',
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
    return redirect(url_for('administration.groups.index'))


@module.route('/<group_id>/edit', methods=["GET", "POST"])
@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
def edit_usergroup(group_id):
    group = models.UserGroup.objects.get(id=group_id)

    form = UserGroupForm(obj=group)
    if not form.validate_on_submit():
        return render_template('/administration/groups/create-edit.html',
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

    return redirect(url_for('administration.groups.index'))


@module.route('/create_doorgroup', methods=["GET", "POST"])
@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
def create_doorgroup():
    form = DoorGroupForm()
    if not form.validate_on_submit():
        return render_template('/administration/groups/create-edit.html',
                               form=form)
    door_group = models.DoorGroup()
    form.populate_obj(door_group)

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
    return redirect(url_for('administration.doors.index'))


@module.route('/<doorgroup_id>/edit_doorgroup', methods=["GET", "POST"])
@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
def edit_doorgroup(doorgroup_id):
    group = models.DoorGroup.objects.get(id=doorgroup_id)

    form = DoorGroupForm(obj=group)
    if not form.validate_on_submit():
        return render_template('/administration/groups/create-edit.html',
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

    return redirect(url_for('administration.doors.index'))


@module.route('user_group/<group_id>/delete')
@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
def delete_usergroup(group_id):
    selected_group = models.UserGroup.objects.get(id=group_id)
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

    return redirect(url_for('administration.groups.index'))


@module.route('door_group/<doorgroup_id>/delete')
@acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
def delete_doorgroup(doorgroup_id):
    group = models.DoorGroup.objects.get(id=doorgroup_id)
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

    return redirect(url_for('administration.doors.index'))
