from flask import Blueprint, render_template, url_for, request, Response, redirect, g
from flask_login import login_required, current_user
from pichayon import models
import json
import datetime
from pichayon.web import pichayon_client

module = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@module.route("/")
@login_required
def index():
    if not current_user.gave_informations:
        return redirect(url_for("accounts.edit_profile"))

    user_group_members = models.UserGroupMember.objects(
        user=current_user._get_current_object(),
    )

    user_groups = [m.group for m in user_group_members]
    group_auths = models.GroupAuthorization.objects(user_group__in=user_groups)

    door_groups = [ga.door_group for ga in group_auths]

    doors = []
    for door_group in door_groups:
        doors.extend(door_group.doors)

    door_states = dict()
    doors = set(doors)

    for door in doors:
        if door.device_type == "pichayon":
            door_states[door.id] = door.get_state()
        elif door.device_type == "sparkbit":
            response = pichayon_client.pichayon_client.get_door_state(door, "sparkbit")
            door_states[door.id] = response["door"]["state"]

    return render_template(
        "/dashboard/index.html",
        door_groups=door_groups,
        user_groups=user_groups,
        doors=doors,
        door_states=door_states,
    )


@module.route("/open_door", methods=("GET", "POST"))
@login_required
def open_door():
    door_id = request.form.get("door_id")
    # user_group_id = request.form.get('user_group_id')
    door = models.Door.objects.get(id=door_id)
    # print(door_id)
    pichayon_client.pichayon_client.open_door(
        door,
        current_user,
        ip=request.headers.get("X-Forwarded-For", request.remote_addr),
    )

    response = Response()
    response.status_code = 200
    return response
