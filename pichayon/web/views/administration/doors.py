from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   request,
                   g)

from pichayon import models
from pichayon.web import acl
from pichayon.web.forms.admin import DoorForm, DoorGroupForm
from flask_login import login_user, logout_user, login_required, current_user
module = Blueprint('administration.doors',
                   __name__,
                   url_prefix='/doors')


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    door_groups = models.DoorGroup.objects(status='active').order_by('name')
    return render_template('/administration/doors/index.html',
                           door_groups=door_groups)


@module.route('/create', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def create():
    form = DoorForm()
    if not form.validate_on_submit():
        return render_template('/administration/doors/create-edit.html',
                               form=form)
    door = models.Door()
    form.populate_obj(door)
    door.creator = current_user._get_current_object()
    door.save()
    group_id = request.args.get('group_id')
    door_group = models.DoorGroup.objects.get(id=group_id)
    door_group.members.append(door)
    door_group.save()
    return redirect(url_for('administration.groups.door_group',
                            doorgroup_id=group_id))


@module.route('/<doorgroup_id>/doorlists', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def doors_list(doorgroup_id):
    door_group = models.DoorGroup.objects.get(id=doorgroup_id)
    return render_template('/administration/doors/door_lists.html',
                           door_group=door_group)


@module.route('/<door_id>/edit', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def edit(door_id):
    door = models.Door.objects.get(id=door_id)

    form = DoorForm(obj=door)
    if not form.validate_on_submit():
        return render_template('/administration/doors/create-edit.html',
                               form=form)

    form.populate_obj(door)
    door.save()

    return redirect(url_for('administration.doors.index'))


@module.route('/<door_id>/delete')
@acl.allows.requires(acl.is_admin)
def delete(door_id):
    door = models.Door.objects.get(id=door_id)
    door.status = 'delete'
    door.save()

    return redirect(url_for('administration.doors.index'))
