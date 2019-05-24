from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

import datetime

from pichayon.web import acl
from pichayon.web.forms.admin import (UserForm,
                                      AddingUserForm,
                                      AddingRoomForm)

module = Blueprint('admin.users',
                   __name__,
                   url_prefix='/users')


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    pichayon_client = g.get_pichayon_client()
    users = pichayon_client.users.list()
    # for user in users:
        # print(user.email)
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

    return redirect(url_for('admin.users.index'))


@module.route('/<user_id>/grant', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def grant(user_id):
    pichayon_client = g.get_pichayon_client()
    user = pichayon_client.users.get(user_id)
    rooms = pichayon_client.rooms.list()
    form = AddingRoomForm()
    form.started_date.data = datetime.datetime.now()
    form.expired_date.data = datetime.datetime.now()

    form.room.choices = [(room.id, room.name) for room in rooms]

    
    # print(form.validate_on_submit())
    if not form.validate_on_submit():
        return render_template('/dashboard/admin/users/grant.html',
                               form=form,
                               user=user,
                               rooms=rooms)


    # print(form.data)
    user = pichayon_client.authorizations.create(**form.data)
    if user.is_error:
        return render_template('/dashboard/admin/users/grant.html',
                               form=form,
                               user=user,
                               rooms=rooms)

    return redirect(url_for('admin.users.index'))


@module.route('/<user_id>/delete')
@acl.allows.requires(acl.is_admin)
def delete(user_id):
    pichayon_client = g.get_pichayon_client()
    pichayon_client.users.delete(user_id)

    return redirect(url_for('admin.users.index'))
