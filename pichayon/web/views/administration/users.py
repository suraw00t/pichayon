from flask import Blueprint, render_template, redirect, url_for, request, g

import datetime
from flask_login import login_user, logout_user, login_required, current_user
from pichayon import models
from pichayon.web import (
    acl,
    forms,
)
from pichayon.web.client.pichayon_client import pichayon_client

from pichayon.web.forms.admin import (
    UserForm,
    AddingUserForm,
    AddRoleUserForm,
    EditForm,
    AddingRoomForm,
)
import string
import random
import json

module = Blueprint("users", __name__, url_prefix="/users")


def generate_passcode():
    res = "".join(random.choices("ABCD" + string.digits, k=6))
    return str(res)


@module.route("/")
@acl.admin_permission.require(http_exception=403)
def index():
    users = models.User.objects().order_by("username", "role")
    return render_template("/administration/users/index.html", users=users)


@module.route("/<user_group_id>/users_list", methods=["GET", "POST"])
@acl.admin_permission.require(http_exception=403)
def list(user_group_id):
    group = models.UserGroup.objects.get(id=user_group_id)
    return render_template("administration/groups/users_list.html", group=group)


@module.route("/<user_group_id>/adduser", methods=["GET", "POST"])
@acl.admin_permission.require(http_exception=403)
def add(user_group_id):

    group = models.UserGroup.objects.get(id=user_group_id)
    users = models.User.objects(status="active")
    form = AddingUserForm()
    choices = []
    for user in users:
        if not group.is_user_member(user):
            choices.append((user.username, user.username))
    choices.sort()
    form.username.choices = choices
    if not form.validate_on_submit():
        return render_template(
            "administration/users/adding_user.html", form=form, group=group
        )
    for username in form.username.data:
        user = models.User.objects.get(username=username)
        if group.is_user_member(user):
            continue
        member = models.UserGroupMember(
            group=group,
            user=user,
            added_by=current_user._get_current_object(),
            added_date=datetime.datetime.now(),
        )
        if "supervisor" in user.roles:
            member.role = "supervisor"
        member.save()

    return redirect(url_for("users.list", group_id=group_id))


@module.route("/<user_group_id>/add_role", methods=["GET", "POST"])
@acl.admin_permission.require(http_exception=403)
def add_role(user_group_id):
    group = models.UserGroup.objects.get(id=user_group_id)
    user_id = request.args.get("user_id")
    user = models.User.objects.get(id=user_id)
    form = AddRoleUserForm()
    form.role.choices = [("supervisor", "Supervisor"), ("member", "Member")]
    for member in group.get_user_group_members():
        if user == member.user:
            selected_member = member
            break

    if not form.validate_on_submit():
        form.role.data = selected_member.role
        return render_template(
            "administration/users/add_role.html", group=group, form=form
        )
    user_group = models.UserGroupMember.objects.get(user=user, group=group)
    user_group.role = form.role.data
    user_group.save()
    if "Supervisor" in form.role.data and "Supervisor" not in user.roles:
        user.roles.append("supervisor")
        user.save()

    return redirect(url_for("users.list", group_id=group_id))


@module.route("/<group_id>/deleteuser", methods=["GET", "POST"])
@acl.admin_permission.require(http_exception=403)
def delete(group_id):
    group = models.UserGroup.objects.get(id=group_id)
    user_id = request.args.get("user_id")
    user = models.User.objects.get(id=user_id)
    for member in group.members:
        if member.user == user:
            group.members.remove(member)
            break
    group.save()

    return redirect(url_for("administration.users.list", group_id=group_id))


@module.route("/<user_id>/edit", methods=["GET", "POST"])
@acl.admin_permission.require(http_exception=403)
def edit(user_id):
    user = models.User.objects.get(id=user_id)
    form = EditForm(obj=user)
    form.roles.choices = [
        ("admin", "Admin"),
        ("supervisor", "Supervisor"),
        ("student", "Student"),
        ("user", "User"),
    ]
    if not form.validate_on_submit():
        return render_template("administration/users/edit.html", form=form, user=user)
    user.roles = form.roles.data
    user.save()
    return redirect(url_for("administration.users.index"))


@module.route("/<user_id>/revoke_passcode", methods=["GET", "POST"])
@acl.role_required("admin")
def revoke_passcode(user_id):
    user = models.User.objects.get(id=user_id)
    passcode = generate_passcode()
    user_passcode = models.User.objects(passcode=passcode).first()
    while user_passcode:
        passcode = generate_passcode()
        user_passcode = models.User.objects(passcode=passcode).first()

    user.passcode = passcode
    user.save()
    return redirect(url_for("administration.users.index"))


@module.route("/<user_id>/identities", methods=["GET", "POST"])
@login_required
def identity(user_id):
    user = models.User.objects.get(id=user_id)
    return render_template(
        "administration/users/identity.html",
        user=user,
    )


@module.route(
    "/<user_id>/identities/add", methods=["GET", "POST"], defaults={"index": -1}
)
@module.route("/<user_id>/identities/<int:index>/edit", methods=["GET", "POST"])
@login_required
def add_or_edit_identity(user_id, index):
    user = models.User.objects.get(id=user_id)

    form = forms.admin.users.IdentityForm()
    if request.method == "GET" and index >= 0:
        form = forms.admin.users.IdentityForm(obj=user.identities[index])

    if not form.validate_on_submit():
        return render_template(
            "administration/users/add-edit-identity.html",
            form=form,
        )

    identity = models.Identity()
    if index >= 0:
        identity = user.identities[index]

    form.populate_obj(identity)

    if index < 0:
        is_found = False
        for idr in user.identities:
            if idr.identifier == form.identifier.data:
                is_found = True
                break
        if not is_found:
            user.identities.append(identity)

    user.save()

    pichayon_client.update_member(user)

    return redirect(
        url_for(
            "administration.users.identity",
            user_id=user_id,
        )
    )


@module.route("/<user_id>/identities/<int:index>/delete")
@login_required
def delete_identity(user_id, index):
    user = models.User.objects.get(id=user_id)

    if index < len(user.identities):
        user.identities.pop(index)

    user.save()
    pichayon_client.update_member(user)

    return redirect(
        url_for(
            "administration.users.identity",
            user_id=user_id,
        )
    )
