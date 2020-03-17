from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   request,
                   g)

import datetime
from flask_login import login_user, logout_user, login_required, current_user
from pichayon import models
from pichayon.web import acl
from pichayon.web.forms.admin import (UserForm,
                                      AddingUserForm,
                                      AddRoleUserForm,
                                      EditForm,
                                      AddingRoomForm)
import string
import random
module = Blueprint('administration.users',
                   __name__,
                   url_prefix='/users')


def generate_passcode():
    res = ''.join(random.choices('ABCD' + string.digits, k=6))
    return str(res)


@module.route('/')
@acl.allows.requires(acl.is_admin)
def index():
    users = models.User.objects().order_by('username', 'role')
    return render_template('/administration/users/index.html',
                           users=users)


@module.route('/<group_id>/users_list', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def list(group_id):
    group = models.UserGroup.objects.get(id=group_id)
    return render_template('administration/groups/users_list.html',
                           group=group)


@module.route('/<group_id>/adduser', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def add(group_id):

    group = models.UserGroup.objects.get(id=group_id)
    users = models.User.objects(status='active')
    form = AddingUserForm()
    choices = []
    for user in users:
        if not group.is_user_member(user):
            choices.append((user.username, user.username))
    choices.sort()
    form.username.choices = choices
    if not form.validate_on_submit():
        return render_template('administration/users/adding_user.html',
                               form=form,
                               group=group)
    for username in form.username.data:
        user = models.User.objects.get(username=username)
        if group.is_user_member(user):
            continue
        member = models.UserGroupMember(
                group=group,
                user=user,
                added_by=current_user._get_current_object(),
                added_date=datetime.datetime.now())
        if 'supervisor' in user.roles:
            member.role = 'supervisor'
        member.save()

    return redirect(url_for('administration.users.list', group_id=group_id))


@module.route('/<group_id>/add_role', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def add_role(group_id):
    group = models.UserGroup.objects.get(id=group_id)
    user_id = request.args.get('user_id')
    user = models.User.objects.get(id=user_id)
    form = AddRoleUserForm()
    form.role.choices = [('supervisor', 'Supervisor'), ('member', 'Member')]
    for member in group.get_user_group_members():
        if user == member.user:
            selected_member = member
            break

    if not form.validate_on_submit():
        form.role.data = selected_member.role
        return render_template('administration/users/add_role.html',
                               group=group,
                               form=form)
    user_group = models.UserGroupMember.objects.get(user=user, group=group)
    user_group.role = form.role.data
    user_group.save()
    if 'Supervisor' in form.role.data and 'Supervisor' not in user.roles:
        user.roles.append('supervisor')
        user.save()


    return redirect(url_for('administration.users.list', group_id=group_id))

@module.route('/<group_id>/deleteuser', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def delete(group_id):
    group = models.UserGroup.objects.get(id=group_id)
    user_id = request.args.get('user_id')
    user = models.User.objects.get(id=user_id)
    for member in group.members:
        if member.user == user:
            group.members.remove(member)
            break
    group.save()

    return redirect(url_for('administration.users.list', group_id=group_id))


@module.route('/<user_id>/edit', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def edit(user_id):
    user = models.User.objects.get(id=user_id)
    form = EditForm(obj=user)
    form.roles.choices = [('admin', 'Admin'), ('supervisor', 'Supervisor'), ('student', 'Student')]
    if not form.validate_on_submit():
        form.roles.data = user.roles[-1]
        return render_template('administration/users/edit.html',
                               form=form,
                               user=user)
    user.roles[-1] = form.roles.data
    user.rfid = form.rfid.data
    user.save()
    return redirect(url_for('administration.users.index'))


@module.route('/<user_id>/revoke_passcode', methods=["GET", "POST"])
@acl.allows.requires(acl.is_admin)
def revoke_passcode(user_id):
    user = models.User.objects.get(id=user_id)
    passcode = generate_passcode()
    user_passcode = models.User.objects(passcode=passcode).first()
    while (user_passcode):
        passcode = generate_passcode()
        user_passcode = models.User.objects(passcode=passcode).first()

    user.passcode = passcode
    user.save()
    return redirect(url_for('administration.users.index'))

