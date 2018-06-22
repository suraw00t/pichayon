from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

import datetime

from pichayon.web import acl
from pichayon.web.forms.admin import (UserForm,
                                      AddingUserForm,
                                      AddingRoomForm,
                                      AuthorizedRoomForm)
from pichayon.client.resources import User
from pichayon.client.resources import Authorization

module = Blueprint('web.dashboard.admin.users',
                   __name__,
                   url_prefix='/users')


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    pichayon_client = g.get_pichayon_client()
    users = pichayon_client.users.list()
    return render_template('/dashboard/admin/users/index.html',
                           users=users)


@module.route('/create', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def create():
    pichayon_client = g.get_pichayon_client()
    form = AddingUserForm()
    if not form.validate_on_submit():
        return render_template('/dashboard/admin/users/create.html',
                               form=form)
    user = pichayon_client.users.create(**form.data)

    if user.is_error:
        return render_template('/dashboard/admin/users/create.html',
                               form=form)

    return redirect(url_for('web.dashboard.admin.users.index'))


@module.route('/<user_id>/grant', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def grant(user_id):
    pichayon_client = g.get_pichayon_client()
    user = pichayon_client.users.get(user_id)
    # print(user)
    # print(user.username)
    rooms = pichayon_client.rooms.list()
    # room_choices = [(room.id, room.name) for room in rooms]
    # form = AddingRoomForm(obj=user)
    # print(user)
    # form.room.choices = room_choices
    form = AuthorizedRoomForm()
    from wtforms import fields
    # print(room.name)
    for room  in rooms:
        # print(room.name)
        f = AddingRoomForm()
        f.room.data = room.id
        f.room.label.text = room.name
        f.room = fields.HiddenField(room.name, default=room.id)
        # print(f.room.label.__dict__)
        f.started_date = datetime.datetime.now()
        f.expired_date = datetime.datetime.now()
        form.rooms.append_entry(f)

    
    # print(form.rooms)
    if not form.validate_on_submit():
        return render_template('/dashboard/admin/users/grant.html',
                               form=form,
                               user=user,
                               rooms=rooms)


    print(form.data)
    user = pichayon_client.authorizations.create(**form.data)

    if user.is_error:
        return render_template('/dashboard/admin/users/grant.html',
                               form=form,
                               user=user,
                               rooms=rooms)

    return redirect(url_for('web.dashboard.admin.users.index'))


@module.route('/<user_id>/delete')
@acl.allows.requires(acl.is_admin)
def delete(user_id):
    pichayon_client = g.get_pichayon_client()
    pichayon_client.users.delete(user_id)

    return redirect(url_for('web.dashboard.admin.users.index'))
