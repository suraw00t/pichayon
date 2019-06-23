from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

from pichayon import models
from pichayon.web import acl
from pichayon.web.forms.admin import DoorForm

module = Blueprint('administration.doors',
                   __name__,
                   url_prefix='/doors')


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    doors = models.Door.objects(status='active')
    return render_template('/administration/doors/index.html',
                           doors=doors)


@module.route('/create', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def create():
    form = DoorForm()
    if not form.validate_on_submit():
        return render_template('/administration/doors/create-edit.html',
                               form=form)
    door = models.Door()
    form.populate_obj(door)

    door.save()

    return redirect(url_for('administration.doors.index'))


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
