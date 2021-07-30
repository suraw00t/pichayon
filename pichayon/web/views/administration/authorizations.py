from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   request,
                   g)

from pichayon import models
from pichayon.web import acl
from pichayon.web.forms.admin import AuthorityForm
from flask_login import login_user, logout_user, login_required, current_user

import datetime
module = Blueprint('authorizations',
                   __name__,
                   url_prefix='/auths')


@module.route('')
@acl.role_required('admin')
def index():
    group_auth = models.GroupAuthorization.objects()
    return render_template('/administration/authorizations/index.html',
                           group_auth=group_auth
                           )


@module.route('/add', methods=["GET", "POST"], defaults={'auth_id': None})
@module.route('/<auth_id>/edit', methods=["GET", "POST"], )
@acl.role_required('admin')
def add_or_edit(auth_id):
    door_groups = models.DoorGroup.objects()
    user_groups = models.UserGroup.objects()

    form = AuthorityForm()
    group_auth = None
    if auth_id:
        group_auth = models.GroupAuthorization.objects.get(id=auth_id)

    if group_auth and request.method == 'GET':
        form = AuthorityForm(obj=group_auth)
        form.start_time.data = datetime.time(
                group_auth.rrule.start_time[0], 
                group_auth.rrule.start_time[1],
                group_auth.rrule.start_time[2],
                )
        form.end_time.data = datetime.time(
                group_auth.rrule.end_time[0], 
                group_auth.rrule.end_time[1],
                group_auth.rrule.end_time[2],
                )
        form.days.data = group_auth.rrule.days

    form.door_group.choices = [(str(d.id), d.name) for d in door_groups]
    form.user_group.choices = [(str(u.id), u.name) for u in user_groups]

    if not form.validate_on_submit():
        return render_template('/administration/authorizations/add_authority.html',
                               form=form,
                               )
    # print(form.end_time.data)
    # print(form.start_time.data)
    if not group_auth:
        print('hear')
        group_auth = models.GroupAuthorization()

    print('---->', group_auth)
    rrule = models.Rrule()
    days = []
    for d in form.days.data:
        days.append(int(d))
    rrule.days = days

    start_time = form.start_time.data
    end_time = form.end_time.data

    rrule.start_time = [start_time.hour, start_time.minute, start_time.second]
    rrule.end_time = [start_time.hour, start_time.minute, start_time.second]

    user_group = models.UserGroup.objects.get(id=form.user_group.data)
    door_group = models.DoorGroup.objects.get(id=form.door_group.data)

    group_auth.door_group = door_group
    group_auth.user_group = user_group
    group_auth.granter = current_user._get_current_object()
    group_auth.rrule = rrule
    group_auth.started_date = form.started_date.data
    group_auth.expired_date = form.expired_date.data

    group_auth.save()
    return redirect(
            url_for('administration.authorizations.index')
            )


# @acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
@acl.role_required('admin')
def edit(auth_id):
    group_auth = models.GroupAuthorization.objects.get(id=auth_id)

    form = AuthorityForm(obj=group_auth)
    selected_groupmember = None
    rrule = None
    for group_member in door_auth.authorization_groups:
        if group_member.user_group == user_group:
            selected_groupmember = group_member
            rrule = group_member.rrule
    choices = [(str(user_group.id), user_group.name)]
    form.user_group.choices = choices
    if not form.validate_on_submit():
        h_start, m_start, _ = rrule.start_time.split(':')
        h_end, m_end, _ = rrule.end_time.split(':')
        form.days.data = [str(d) for d in rrule.days]
        form.start_time.data = datetime.time(int(h_start), int(m_start))
        form.end_time.data = datetime.time(int(h_end), int(m_end))
        form.user_group.data = choices[0]
        form.started_date.data = selected_groupmember.started_date
        form.expired_date.data = selected_groupmember.expired_date
        return render_template('/administration/authorizations/edit_authority.html',
                               form=form,
                               door_group=door_group,
                               door_auth=door_auth)

    for group_member in door_auth.authorization_groups:
        if group_member.user_group == user_group:
            group_member.started_date = form.started_date.data
            group_member.expired_date = form.expired_date.data
            group_member.rrule.days = [int(d) for d in form.days.data]
            group_member.rrule.start_time = str(form.start_time.data)
            group_member.rrule.end_time = str(form.end_time.data)
    door_auth.save()
    return redirect(url_for('administration.door_authorizations.index',
                            group_id=doorgroup_id))


@module.route('/<auth_id>/delete', methods=["GET", "POST"])
@acl.role_required('admin')
def delete(auth_id):
    group_auth = models.GroupAuthorization.objects.get(
            id=auth_id)
    if group_auth:
        group_auth.delete()

    return redirect(
            url_for('administration.authorizations.index'))
