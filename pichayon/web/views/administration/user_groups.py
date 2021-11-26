from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   g)

from flask_login import login_user, logout_user, login_required, current_user
from pichayon import models
from pichayon.web import acl, forms, nats
from pichayon.web.forms.admin import DoorGroupForm, UserGroupForm
import datetime
import json


module = Blueprint('user_groups',
                   __name__,
                   url_prefix='/users/groups')


@module.route('')
@acl.role_required('admin')
def index():
    groups = models.UserGroup.objects(status='active').order_by('name')
    return render_template('/administration/user_groups/index.html',
                           groups=groups)


@module.route('/create', methods=["GET", "POST"], defaults={"user_group_id": None})
@module.route('/<user_group_id>/edit', methods=["GET", "POST"])
@acl.role_required('admin')
def create_or_edit(user_group_id=None):
    form = UserGroupForm()

    group = None
    if user_group_id:
        user_group = models.UserGroup.objects(id=user_group_id).first()
        form = UserGroupForm(obj=user_group)
    
    if not form.validate_on_submit():
        return render_template('/administration/user_groups/create-edit.html',
                               form=form)

    if not user_group:
        user_group = models.UserGroup()

    form.populate_obj(user_group)
    user_group.creator = current_user._get_current_object()
    user_group.save()

    return redirect(url_for('administration.user_groups.index'))


@module.route('/<user_group_id>')
@acl.role_required('admin')
def view(user_group_id):
    group = models.UserGroup.objects.get(id=user_group_id)

    form = forms.admin.groups.UserGroupMemberForm()
    users = models.User.objects.all()

    form.users.choices = [(str(u.id), f'{u.username} - {u.first_name} {u.last_name}') for u in users]

    return render_template('/administration/user_groups/view.html',
                           group=group,
                           form=form,
                           )

@module.route('/<user_group_id>/delete')
@acl.role_required('admin')
def delete(user_group_id):
    group = models.UserGroup.objects.get(id=user_group_id)
    models.GroupAuthorization.objects(user_group=group).delete()

    # group.status = 'delete'
    models.UserGroupMember.objects(
            group=group,
            ).delete()

    group.delete()

    return redirect(url_for('administration.user_groups.index'))


@module.route('/<user_group_id>/add_member', methods=['POST'])
def add_member(user_group_id):
    form = forms.admin.groups.UserGroupMemberForm()
    
    group = models.UserGroup.objects(id=user_group_id).first()
    users = models.User.objects.all()

    form.users.choices = [
            (str(u.id), f'{u.username} - {u.first_name} {u.last_name}') for u in users]
    if not form.validate_on_submit():
        return redirect(url_for('administration.user_groups.view', user_group_id=user_group_id))

    if not group:
        return redirect(url_for('administration.user_groups.index'))

    for uid in form.users.data:
        user = models.User.objects(id=uid).first()
        if not user:
            continue

        member = models.UserGroupMember.objects(
                user=user,
                group=group,
                ).first()

        if not member:
            member = models.UserGroupMember(
                    user=user,
                    group=group,
                    added_by=current_user._get_current_object(),
                    )

        member.role = form.role.data
        member.started_date = form.started_date.data
        member.expired_date = form.expired_date.data
        
        member.save()


    # add data in group
    data = json.dumps({
            'action': 'add-member-to-group',
            'user_group_id': str(group.id),
            'user_ids': form.users.data,
        })
    nats.nats_client.publish(
        'pichayon.controller.command',
        data
        )
    return redirect(url_for('administration.user_groups.view', user_group_id=user_group_id))

@module.route('/<user_group_id>/delete_user/<member_id>')
def delete_member(user_group_id, member_id):
    member = models.UserGroupMember.objects(
            id=member_id).first()
    user = member.user

    if member:
        member.delete()

    data = json.dumps({
            'action': 'delete-member-from-group',
            'user_group_id': str(user_group_id),
            'user_id': str(user.id),
        })
    nats.nats_client.publish(
        'pichayon.controller.command',
        data
        )

    return redirect(url_for('administration.user_groups.view', user_group_id=user_group_id))

