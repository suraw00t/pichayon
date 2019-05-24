from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

from pichayon.web import acl
from pichayon.web.forms.admin import RoomForm

module = Blueprint('admin.rooms',
                   __name__,
                   url_prefix='/rooms')


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    pichayon_client = g.get_pichayon_client()
    rooms = pichayon_client.rooms.list()
    return render_template('/admin/rooms/index.html',
                           rooms=rooms)


@module.route('/create', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def create():
    pichayon_client = g.get_pichayon_client()
    rooms = pichayon_client.rooms.list()
    form = RoomForm()
    if not form.validate_on_submit():
        return render_template('/admin/rooms/create.html',
                               form=form)

    room = pichayon_client.rooms.create(**form.data)

    if room.is_error:
        return render_template('/admin/rooms/create.html',
                               form=form)

    return redirect(url_for('admin.rooms.index'))


@module.route('/<room_id>/update', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def update(room_id):
    pichayon_client = g.get_pichayon_client()
    room = pichayon_client.rooms.get(room_id)

    form = RoomForm(obj=room)
    if not form.validate_on_submit():
        return render_template('/admin/rooms/create.html',
                               form=form)

    room = Room(id=room_id, **form.data)
    room = pichayon_client.rooms.update(room)

    if room.is_error:
        return render_template('/admin/rooms/create.html',
                               form=form)

    return redirect(url_for('admin.rooms.index'))


@module.route('/<room_id>/delete')
@acl.allows.requires(acl.is_admin)
def delete(room_id):
    pichayon_client = g.get_pichayon_client()
    pichayon_client.rooms.delete(room_id)

    return redirect(url_for('admin.rooms.index'))
