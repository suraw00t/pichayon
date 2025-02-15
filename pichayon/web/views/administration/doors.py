from flask import Blueprint, render_template, redirect, url_for, request, g

from pichayon import models
from pichayon.web import acl, pichayon_client
from pichayon.web.forms.admin import DoorForm, DoorGroupForm
from flask_login import login_user, logout_user, login_required, current_user

import string
import random
import json
import datetime

module = Blueprint("doors", __name__, url_prefix="/doors")


@module.route("")
@acl.role_required("admin")
def index():
    doors = models.Door.objects(status="active").order_by("name")
    return render_template("/administration/doors/index.html", doors=doors)


@module.route("/create", methods=["GET", "POST"], defaults=dict(door_id=None))
@module.route("/<door_id>/edit", methods=["GET", "POST"])
@acl.role_required("admin")
def create_or_edit(door_id):
    form = DoorForm()

    door = None
    if door_id:
        door = models.Door.objects.get(id=door_id)
        form = DoorForm(obj=door)

    form.device_type.choices = [("pichayon", "Pichayon"), ("sparkbit", "Sparkbit")]
    door_groups = models.DoorGroup.objects()

    if not form.validate_on_submit():
        if request.method == "GET":
            if door:
                form.begin_access_time.data = door.begin_access_time.time()
                form.end_access_time.data = door.end_access_time.time()
            else:
                form.begin_access_time.data = "00:00"
                form.end_access_time.data = "00:00"

        return render_template(
            "/administration/doors/create-edit.html",
            form=form,
            door_groups=door_groups,
        )

    if not door:
        door = models.Door()
        door.creator = current_user._get_current_object()

    if form.begin_access_time.data:
        form.begin_access_time.data = datetime.datetime.combine(
            door.begin_access_time.date(), form.begin_access_time.data
        )

    if form.end_access_time.data:
        form.end_access_time.data = datetime.datetime.combine(
            door.begin_access_time.date(), form.end_access_time.data
        )

    form.populate_obj(door)
    door.updater = current_user._get_current_object()
    door.updated_date = datetime.datetime.now()

    # if form.have_passcode.data:
    # door /.passcode = generate_passcode()

    door.save()

    door_group = models.DoorGroup.objects(doors=door).first()

    if not door_group:
        door_group = models.DoorGroup(
            name=f"Default {door.name}",
            default=True,
            creator=current_user._get_current_object(),
            doors=[door],
        )
        door_group.save()

    if form.device_type.data == "sparkbit":
        sparkbit_system = models.SparkbitDoorSystem.objects(door=door).first()
        if not sparkbit_system:
            sparkbit_system = models.SparkbitDoorSystem()
            sparkbit_system.creator = current_user._get_current_object()
            sparkbit_system.door = door

        form.populate_obj(sparkbit_system)
        sparkbit_system.name = f"{form.name.data}"
        sparkbit_system.status = "active"
        sparkbit_system.save()
    else:
        sparkbit_system = models.SparkbitDoorSystem.objects(door=door).first()
        if sparkbit_system:
            sparkbit_system.delete()

    if door.device_type == "pichayon" and "edit" in request.path:
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        pichayon_client.pichayon_client.update_door_information(
            door,
            current_user,
            ip=ip,
        )

    # door_group.members.append(door)
    # door_group.save()
    return redirect(url_for("administration.doors.index"))


@module.route("/<door_group_id>/doors_list", methods=["GET", "POST"])
@acl.role_required("admin")
def list():
    doors = models.Door.objects.all()
    return render_template(
        "/administration/doors/list.html",
        doors=doors,
    )


@module.route("/<door_id>")
@acl.role_required("admin")
def view(door_id):
    door = models.Door.objects.get(id=door_id)
    return render_template(
        "/administration/doors/view.html",
        door=door,
    )


@module.route("/<door_id>/delete")
@acl.role_required("admin")
def delete(door_id):
    door = models.Door.objects.get(id=door_id)

    door_groups = models.DoorGroup.objects(doors=door)
    for dg in door_groups:
        if door.name in dg.name and dg.default:
            group_auth = models.GroupAuthorization.objects(door_group=dg).first()
            if group_auth:
                group_auth.delete()
            dg.delete()

    sb_door_systems = models.SparkbitDoorSystem.objects(
        door=door,
    )
    for ds in sb_door_systems:
        ds.delete()

    door.delete()

    return redirect(url_for("administration.doors.index"))


# @module.route('/<door_id>/revoke_passcode')
# @acl.allows.requires(Or(acl.is_admin, acl.is_supervisor))
# def revoke_passcode(door_id):
#     door = models.Door.objects.get(id=door_id)
#     door.passcode = generate_passcode()
#     door.save()
#     loop = g.get_loop()
#     data = json.dumps({
#         'action': 'update_passcode',
#         'door_id': door_id
#         })
#     nats_client = g.get_nats_client()
#     loop.run_until_complete(nats_client.publish(
#         'pichayon.controller.command',
#         data.encode()
#         ))
#     return redirect(url_for('dashboard.index'))
