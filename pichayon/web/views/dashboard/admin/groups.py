from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

from pichayon.web import acl
from pichayon.web.forms.admin import GroupForm
from pichayon.client.resources import Group

module = Blueprint('web.dashboard.admin.groups',
                   __name__,
                   url_prefix='/groups')


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    pichayon_client = g.get_pichayon_client()
    groups = pichayon_client.groups.list()
    return render_template('/dashboard/admin/groups/index.html',
                           groups=groups)


@module.route('/create', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def create():
    form = GroupForm()
    if not form.validate_on_submit():
        return render_template('/dashboard/admin/groups/create.html',
                               form=form)
    room = pichayon_client.rooms.list()
    pichayon_client = g.get_pichayon_client()
    group = pichayon_client.groups.create(**form.data)

    if group.is_error:
        return render_template('/dashboard/admin/groups/create.html',
                               form=form)

    return redirect(url_for('web.dashboard.admin.groups.index'))


@module.route('/<group_id>/update', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def update(group_id):
    pichayon_client = g.get_pichayon_client()
    group = pichayon_client.groups.get(group_id)

    form = GroupForm(obj=group)
    if not form.validate_on_submit():
        return render_template('/dashboard/admin/groups/create.html',
                               form=form)

    group = Group(id=group_id, **form.data)
    group = pichayon_client.groups.update(group)

    if group.is_error:
        return render_template('/dashboard/admin/groups/create.html',
                               form=form)

    return redirect(url_for('web.dashboard.admin.groups.index'))


@module.route('/<group_id>/delete')
@acl.allows.requires(acl.is_admin)
def delete(group_id):
    pichayon_client = g.get_pichayon_client()
    pichayon_client.groups.delete(group_id)

    return redirect(url_for('web.dashboard.admin.groups.index'))
