from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

from pichayon.web import acl
from pichayon.web.forms.admin import DoorForm
from pichayon.client.resources import Door

module = Blueprint('web.dashboard.admin.doors',
                   __name__,
                   url_prefix='/doors')


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    pichayon_client = g.get_pichayon_client()
    doors = pichayon_client.doors.list()
    return render_template('/dashboard/admin/doors/index.html',
                           doors=doors)


@module.route('/create', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def create():
    form = DoorForm()
    if not form.validate_on_submit():
        return render_template('/dashboard/admin/doors/create.html',
                               form=form)
    pichayon_client = g.get_pichayon_client()
    door = pichayon_client.doors.create(**form.data)

    if door.is_error:
        return render_template('/dashboard/admin/doors/create.html',
                               form=form)

    return redirect(url_for('web.dashboard.admin.doors.index'))


@module.route('/<door_id>/update', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def update(door_id):
    pichayon_client = g.get_pichayon_client()
    door = pichayon_client.doors.get(door_id)

    form = DoorForm(obj=door)
    if not form.validate_on_submit():
        return render_template('/dashboard/admin/doors/create.html',
                               form=form)

    door = Door(id=door_id, **form.data)
    door = pichayon_client.doors.update(door)

    if door.is_error:
        return render_template('/dashboard/admin/doors/create.html',
                               form=form)

    return redirect(url_for('web.dashboard.admin.doors.index'))


@module.route('/<door_id>/delete')
@acl.allows.requires(acl.is_admin)
def delete(door_id):
    pichayon_client = g.get_pichayon_client()
    pichayon_client.doors.delete(door_id)

    return redirect(url_for('web.dashboard.admin.doors.index'))
