from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

from pichayon.web import acl
from pichayon.web.forms.admin import UserForm, AddingUserForm, AddingRoomForm
from pichayon.client.resources import User
from flask_login import current_user

module = Blueprint('web.dashboard.admin.authorization',
                   __name__,
                   url_prefix='/users/<user_id>/authorizations')

@module.route('/update', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def update(user_id):
    pichayon_client = g.get_pichayon_client()
    user = pichayon_client.users.get(user_id)
    print(user.username)
    rooms = pichayon_client.rooms.list()
    room_choices = [(room.name, room.name) for room in rooms]
    form = AddingRoomForm(obj=user)
    # print(user)
    form.rooms.choices = room_choices
    # print(form.rooms)
    if not form.validate_on_submit():
        return render_template('/dashboard/admin/authorizations/update.html',
                               form=form,
                               user=user)


    user = User(id=user_id, **form.data)
    user = pichayon_client.users.update(user)

    if user.is_error:
        return render_template('/dashboard/admin/authorizations/update.html',
                               form=form,
                               user=user)

    return redirect(url_for('web.dashboard.admin.users.index'))

