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
import datetime
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
        form.start_time.data = datetime.time(11,0)
        return render_template('/administration/authorizations/add_authority.html',
                               form=form,
                               door_group=door_group,
                               door_auth=door_auth)
    print(form.end_time.data)
    print(form.start_time.data)
    rrule = models.Rrule()
    days = []
    for d in form.days.data:
        days.append(int(d))
    rrule.days = days
    rrule.start_time = str(form.start_time.data)
    rrule.end_time = str(form.end_time.data)
    g_name = form.user_group.data
    u_group = models.UserGroup.objects.get(name=g_name)
    group_member = models.GroupMember(group=u_group,
                                      granter=current_user._get_current_object(),
                                      rrule=rrule,
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
    doorgroup_id = request.args.get('doorgroup_id')
    usergroup_id = request.args.get('usergroup_id')
    door_group = models.DoorGroup.objects.get(id=doorgroup_id)
    door_auth = models.DoorAuthorizations.objects.get(door_group=door_group)
    form = AddAuthorityForm(obj=door_auth)
    user_group = models.UserGroup.objects.get(id=usergroup_id)
    selected_groupmember = None
    rrule = None
    for group_member in door_auth.user_group:
        if group_member.group == user_group:
            selected_groupmember = group_member
            rrule = group_member.rrule
    choices = [(str(user_group.id), user_group.name)]
    form.user_group.choices = choices
    if not form.validate_on_submit():
        form.days.data = [str(d) for d in rrule.days]
        form.user_group.data = choices[0]
        form.started_date.data = selected_groupmember.started_date
        form.expired_date.data = selected_groupmember.expired_date
        return render_template('/administration/authorizations/edit_authority.html',
                               form=form,
                               door_group=door_group,
                               door_auth=door_auth)

    for group_member in door_auth.user_group:
        if group_member.group == user_group:
            group_member.started_date = form.started_date.data
            group_member.expired_date = form.expired_date.data
            group_member.rrule.days = [int(d) for d in form.days.data]
    door_auth.save()
    return redirect(url_for('administration.door_authorizations.index',
                            group_id=doorgroup_id))


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
