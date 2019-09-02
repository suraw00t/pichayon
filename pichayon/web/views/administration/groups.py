from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

from pichayon import models
from pichayon.web import acl
from pichayon.web.forms.admin import GroupForm

module = Blueprint('administration.groups',
                   __name__,
                   url_prefix='/groups')


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    groups = models.Group.objects(status='active')
    return render_template('/administration/groups/index.html',
                           groups=groups)


@module.route('/create', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def create():
    form = GroupForm()
    if not form.validate_on_submit():
        return render_template('/administration/groups/create-edit.html',
                               form=form)
    group = models.Group()
    form.populate_obj(group)

    group.save()

    return redirect(url_for('administration.groups.index'))


@module.route('/<group_id>/edit', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def edit(group_id):
    group = models.Group.objects.get(id=group_id)

    form = GroupForm(obj=group)
    if not form.validate_on_submit():
        return render_template('/administration/groups/create-edit.html',
                               form=form)

    form.populate_obj(group)
    group.save()

    return redirect(url_for('administration.groups.index'))


@module.route('/<group_id>/delete')
@acl.allows.requires(acl.is_admin)
def delete(group_id):
    group = models.Group.objects.get(id=group_id)
    group.status = 'delete'
    group.save()

    return redirect(url_for('administration.groups.index'))
