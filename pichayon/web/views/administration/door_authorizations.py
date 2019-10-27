from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   request,
                   g)

from pichayon import models
from pichayon.web import acl
from pichayon.web.forms.admin import AddAuthorityForm
from flask_login import login_user, logout_user, login_required, current_user
module = Blueprint('administration.door_authorizations',
                   __name__,
                   url_prefix='/door_auth')


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    group_id = request.args.get('group_id')
    door_group = models.DoorGroup.objects.get(id=group_id)
    door_auth = models.DoorAuthorizations.objects.get(door_group=door_group)
    return render_template('/administration/authorizations/door_auth.html',
                           door_group=door_group,
                           door_auth=door_auth)


@module.route('add_authority', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def add_authority():
    group_id = request.args.get('group_id')
    door_group = models.DoorGroup.objects.get(id=group_id)
    door_auth = models.DoorAuthorizations.objects.get(door_group=door_group)
    form = AddAuthorityForm()
    user_group = models.UserGroup.objects()
    choices = []
    for group in user_group:
        if not door_auth.is_group_member(group):
            choices.append((group.name, group.name))
    form.user_group.choices = choices
    if not form.validate_on_submit():
        return render_template('/administration/authorizations/add_authority.html',
                               form=form,
                               door_group=door_group,
                               door_auth=door_auth)

    for g_name in form.user_group.data:
        u_group = models.UserGroup.objects.get(name=g_name)
        group_member = models.GroupMember(group=u_group,
                                          granter=current_user._get_current_object(),
                                          started_date=form.started_date.data,
                                          expired_date=form.expired_date.data
                                          )
        door_auth.user_group.append(group_member)
    door_auth.save()
    return redirect(url_for('administration.door_authorizations.index',
                            group_id=group_id))


@module.route('edit_authority', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def edit_authority():
    group_id = request.args.get('group_id')
    door_group = models.DoorGroup.objects.get(id=group_id)
    door_auth = models.DoorAuthorizations.objects.get(door_group=door_group)
    form = AddAuthorityForm(obj=door_auth)
    user_group = models.UserGroup.objects()
    choices = []
    for group in user_group:
        if not door_auth.is_group_member(group):
            choices.append((group.name, group.name))
    form.user_group.choices = choices
    if not form.validate_on_submit():
        return render_template('/administration/authorizations/add_authority.html',
                               form=form,
                               door_group=door_group,
                               door_auth=door_auth)

    for g_name in form.user_group.data:
        u_group = models.UserGroup.objects.get(name=g_name)
        group_member = models.GroupMember(group=u_group,
                                          granter=current_user._get_current_object(),
                                          started_date=form.started_date.data,
                                          expired_date=form.expired_date.data
                                          )
        door_auth.user_group.append(group_member)
    door_auth.save()
    return redirect(url_for('administration.door_authorizations.index',
                            group_id=group_id))


@module.route('delete_authority', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def delete_authority():
    doorgroup_id = request.args.get('doorgroup_id')
    usergroup_id = request.args.get('usergroup_id')
    door_group = models.DoorGroup.objects.get(id=doorgroup_id)
    door_auth = models.DoorAuthorizations.objects.get(door_group=door_group)
    user_group = models.UserGroup.objects.get(id=usergroup_id)
    for ugroup in door_auth.user_group:
        if ugroup.group == user_group:
            door_auth.user_group.remove(ugroup)
            door_auth.save()
    return redirect(url_for('administration.door_authorizations.index',
                            group_id=doorgroup_id))
