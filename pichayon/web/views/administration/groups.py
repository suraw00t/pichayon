from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

from flask_login import login_user, logout_user, login_required, current_user
from pichayon import models
from pichayon.web import acl
from pichayon.web.forms.admin import DoorGroupForm, UserGroupForm

module = Blueprint('administration.groups',
                   __name__,
                   url_prefix='/groups')


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    groups = models.UserGroup.objects(status='active').order_by('name')
    return render_template('/administration/groups/index.html',
                           groups=groups)


@module.route('/create_usergroup', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def create_usergroup():
    form = UserGroupForm()
    if not form.validate_on_submit():
        return render_template('/administration/groups/create-edit.html',
                               form=form)
    user_group = models.UserGroup()
    form.populate_obj(user_group)

    user_group.save()

    return redirect(url_for('administration.groups.index'))


@module.route('/<group_id>/edit', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def edit_usergroup(group_id):
    group = models.UserGroup.objects.get(id=group_id)

    form = UserGroupForm(obj=group)
    if not form.validate_on_submit():
        return render_template('/administration/groups/create-edit.html',
                               form=form)

    form.populate_obj(group)
    group.save()

    return redirect(url_for('administration.groups.index'))


@module.route('/create_doorgroup', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def create_doorgroup():
    form = DoorGroupForm()
    if not form.validate_on_submit():
        return render_template('/administration/groups/create-edit.html',
                               form=form)
    door_group = models.DoorGroup()
    form.populate_obj(door_group)

    door_group.save()
    door_auth = models.DoorAuthorization(door_group=door_group)
    door_auth.save()
    return redirect(url_for('administration.doors.index'))


@module.route('/<doorgroup_id>/edit_doorgroup', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def edit_doorgroup(doorgroup_id):
    group = models.DoorGroup.objects.get(id=doorgroup_id)

    form = DoorGroupForm(obj=group)
    if not form.validate_on_submit():
        return render_template('/administration/groups/create-edit.html',
                               form=form)

    form.populate_obj(group)
    group.save()

    return redirect(url_for('administration.doors.index'))


@module.route('user_group/<group_id>/delete')
@acl.allows.requires(acl.is_admin)
def delete_usergroup(group_id):
    selected_group = models.UserGroup.objects.get(id=group_id)
    door_auths = models.DoorAuthorizations.objects()
    for door_auth in door_auths:
        door_auth.remove_member(selected_group)
    # group.status = 'delete'
    selected_group.delete()

    return redirect(url_for('administration.groups.index'))


@module.route('door_group/<doorgroup_id>/delete')
@acl.allows.requires(acl.is_admin)
def delete_doorgroup(doorgroup_id):
    group = models.DoorGroup.objects.get(id=doorgroup_id)
    # group.status = 'delete'
    door_auth = models.DoorAuthorizations.objects.get(door_group=group)
    door_auth.delete()
    group.delete()

    return redirect(url_for('administration.doors.index'))
