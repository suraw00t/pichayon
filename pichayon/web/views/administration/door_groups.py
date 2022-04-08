from flask import Blueprint, render_template, redirect, url_for, g

from flask_login import login_user, logout_user, login_required, current_user
from pichayon import models
from pichayon.web import acl, forms
from pichayon.web.forms.admin import DoorGroupForm, UserGroupForm
import datetime

module = Blueprint("door_groups", __name__, url_prefix="/doors/groups")


@module.route("")
# @acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
@acl.admin_permission.require(http_exception=403)
def index():
    door_groups = models.DoorGroup.objects(status="active").order_by("name")
    return render_template(
        "/administration/door_groups/index.html", door_groups=door_groups
    )


@module.route("/<door_group_id>")
@acl.role_required("admin")
def view(door_group_id):
    door_group = models.DoorGroup.objects.get(id=door_group_id)

    return render_template(
        "/administration/door_groups/view.html", door_group=door_group
    )


@module.route("/create", methods=["GET", "POST"], defaults={"door_group_id": None})
@module.route("/<door_group_id>/edit", methods=["GET", "POST"])
@acl.role_required("admin")
def create_or_edit(door_group_id):
    form = DoorGroupForm()
    door_group = None
    if door_group_id:
        door_group = models.DoorGroup.objects(id=door_group_id).first()
        form = DoorGroupForm(obj=door_group)

    if not form.validate_on_submit():
        return render_template(
            "/administration/door_groups/create-edit.html", form=form
        )

    if not door_group:
        door_group = models.DoorGroup()
        door_group.creator = current_user._get_current_object()

    form.populate_obj(door_group)
    door_group.save()
    return redirect(url_for("administration.door_groups.index"))


@module.route("/<door_group_id>/delete")
@acl.role_required("admin")
def delete(door_group_id):
    door_group = models.DoorGroup.objects.get(id=door_group_id)
    models.GroupAuthorization.objects(door_group=door_group).delete()

    door_group.delete()
    return redirect(url_for("administration.door_groups.index"))


@module.route("/<door_group_id>/add-door", methods=["GET", "POST"])
@acl.role_required("admin")
def add_door(door_group_id):
    door_group = models.DoorGroup.objects.get(id=door_group_id)
    doors = models.Door.objects(status="active").all()
    form = forms.admin.groups.DoorGroupMemberForm()
    form.doors.choices = [(str(door.id), door.name) for door in doors]

    if not form.validate_on_submit():
        return render_template(
            "administration/door_groups/add-door.html", form=form, door_group=door_group
        )

    for door_id in form.doors.data:
        print("door_id", door_id)
        door = models.Door.objects.get(id=door_id)
        if door not in door_group.doors:
            door_group.doors.append(door)

    door_group.updated_date = datetime.datetime.now()
    door_group.save()

    return redirect(
        url_for("administration.door_groups.view", door_group_id=door_group_id)
    )


@module.route("/<door_group_id>/doors/<door_id>/delete")
@acl.role_required("admin")
def delete_door(door_group_id, door_id):
    door_group = models.DoorGroup.objects.get(id=door_group_id)
    door = models.Door.objects.get(id=door_id)
    door_group.doors.remove(door)
    door_group.save()

    return redirect(
        url_for("administration.door_groups.view", door_group_id=door_group_id)
    )
