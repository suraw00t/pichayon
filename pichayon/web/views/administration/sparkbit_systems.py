from flask import Blueprint, render_template, redirect, url_for, request, g

from pichayon import models
from pichayon.web import acl
from pichayon.web.forms.admin import SparkbitDoorForm
from flask_login import login_user, logout_user, login_required, current_user
import string
import random
import json

module = Blueprint("sparkbit", __name__, url_prefix="/doors/sparkbit")


@module.route("/")
# @acl.allows.requires(acl.is_admin)
@acl.role_required("admin")
def index():
    sparkbit_door_systems = models.SparkbitDoorSystem.objects(status="active").order_by(
        "name"
    )
    return render_template(
        "/administration/sparkbit/index.html",
        sparkbit_door_systems=sparkbit_door_systems,
    )


@module.route("/create", methods=["GET", "POST"])
# @acl.allows.requires(acl.is_admin)
@acl.role_required("admin")
def create():
    form = SparkbitDoorForm()
    doors = models.Door.objects(status="active")
    form.door.choices = [(str(door.id), door.name) for door in doors]
    if not form.validate_on_submit():
        return render_template("/administration/sparkbit/create-edit.html", form=form)
    sparkbit_door = models.SparkbitDoorSystem()
    form.populate_obj(sparkbit_door)
    sparkbit_door.creator = current_user._get_current_object()
    sparkbit_door.door = models.Door.objects.get(id=form.door.data)
    sparkbit_door.save()

    return redirect(url_for("sparkbit.index"))


@module.route("/<sparkbit_door_id>/edit", methods=["GET", "POST"])
# @acl.allows.requires(acl.is_admin)
@acl.role_required("admin")
def edit(sparkbit_door_id):
    doors = models.Door.objects(status="active")
    sparkbit_door = models.SparkbitDoorSystem.objects.get(id=sparkbit_door_id)

    form = SparkbitDoorForm(obj=sparkbit_door)
    form.door.choices = [(str(door.id), door.name) for door in doors]

    if request.method == "GET":
        form.door.data = str(sparkbit_door.id)

    if not form.validate_on_submit():
        print(form.errors)
        print(form.door.choices)
        return render_template("/administration/sparkbit/create-edit.html", form=form)

    form.populate_obj(sparkbit_door)
    sparkbit_door.creator = current_user._get_current_object()
    sparkbit_door.door = models.Door.objects.get(id=form.door.data)
    sparkbit_door.save()

    return redirect(url_for("sparkbit.index"))


@module.route("/<sparkbit_door_id>/delete")
# @acl.allows.requires(acl.is_admin)
@acl.role_required("admin")
def delete(sparkbit_door_id):
    sparkbit_door = models.SparkbitDoorSystem.objects.get(id=sparkbit_door_id)
    if sparkbit_door:
        sparkbit_door.delete()

    return redirect(url_for("doors.index"))
