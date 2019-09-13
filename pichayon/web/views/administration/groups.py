from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

from flask_login import login_user, logout_user, login_required, current_user
from pichayon import models
from pichayon.web import acl
from pichayon.web.forms.admin import DoorGroupForm

module = Blueprint('administration.groups',
                   __name__,
                   url_prefix='/groups')


@module.route('/', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def index():
    return 'group'


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

    return redirect(url_for('administration.groups.index'))


@module.route('/<doorgroup_id>/delete')
@acl.allows.requires(acl.is_admin)
def delete_doorgroup(doorgroup_id):
    group = models.DoorGroup.objects.get(id=doorgroup_id)
    # group.status = 'delete'
    group.delete()

    return redirect(url_for('administration.doors.index'))
