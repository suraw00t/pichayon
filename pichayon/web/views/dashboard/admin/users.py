from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

from pichayon.web import acl
from pichayon.web.forms.admin import UserForm
from pichayon.client.resources import User

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
    form = UserForm()
    if not form.validate_on_submit():
        return render_template('/dashboard/admin/users/create.html',
                               form=form)

    user = pichayon_client.users.create(**form.data)

    if user.is_error:
        return render_template('/dashboard/admin/users/create.html',
                               form=form)

    return redirect(url_for('web.dashboard.admin.users.index'))


@module.route('/<user_id>/update', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def update(user_id):
    pichayon_client = g.get_pichayon_client()
    user = pichayon_client.users.get(user_id)

    form = UserForm(obj=user)
    if not form.validate_on_submit():
        return render_template('/dashboard/admin/users/update.html',
                               form=form)

    user = User(id=user_id, **form.data)
    user = pichayon_client.users.update(user)

    if user.is_error:
        return render_template('/dashboard/admin/users/update.html',
                               form=form)

    return redirect(url_for('web.dashboard.admin.users.index'))


@module.route('/<user_id>/delete')
@acl.allows.requires(acl.is_admin)
def delete(user_id):
    pichayon_client = g.get_pichayon_client()
    pichayon_client.users.delete(user_id)

    return redirect(url_for('web.dashboard.admin.users.index'))
