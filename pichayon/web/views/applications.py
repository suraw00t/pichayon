import datetime

from flask import (
    Blueprint,
    current_app,
    render_template,
    url_for,
    redirect,
    request,
    session,
)

from flask_login import login_user, logout_user, login_required, current_user
from pichayon import models
from .. import forms
from .. import views
from .. import acl

module = Blueprint("applications", __name__, url_prefix="/applications")


@module.route("/")
@login_required
def index():
    user = current_user._get_current_object()
    applications = models.Application.objects(user=user).order_by("-id")
    return render_template("/applications/index.html", applications=applications)


@module.route("/apply", methods=["GET", "POST"])
@login_required
def apply():
    lecturers = models.User.objects(roles="lecturer")
    form = forms.applications.ApplicationForm()
    form.advisor.queryset = lecturers

    user_group_members = models.UserGroupMember.objects(user=current_user)
    user_groups = []
    [
        user_groups.append(ugm.group)
        for ugm in user_group_members
        if ugm not in user_groups
    ]
    group_authorizations = models.GroupAuthorization.objects(
        status="active", user_group__in=user_groups
    )
    door_groups = [ga.door_group for ga in group_authorizations]

    door_id_list = []
    [
        [door_id_list.append(d.id) for d in dg.doors if d not in door_id_list]
        for dg in door_groups
    ]
    doors = models.Door.objects(id__nin=door_id_list)
    form.room.queryset = doors

    if not form.validate_on_submit():
        if request.method == "GET":
            form.ended_date.data = form.started_date.data + datetime.timedelta(
                weeks=52 * 4
            )
        return render_template(
            "/applications/request.html",
            form=form,
        )

    application = models.Application()

    form.populate_obj(application)
    application.user = current_user._get_current_object()

    application.save()

    return redirect(url_for("applications.index"))


@module.route("/approve")
@acl.role_required("lecturer")
def approve():
    user = current_user._get_current_object()
    applications = models.Application.objects(advisor=user).order_by("-id")
    return render_template("/applications/approve.html", applications=applications)


@module.route("/<application_id>/cancel")
@login_required
def cancel(application_id):
    application = models.Application.objects().get(id=application_id)
    application.status = "Canceled"
    application.save()

    return redirect(url_for("applications.index"))


@module.route("/<application_id>/delete")
@login_required
def delete(application_id):
    application = models.Application.objects().get(id=application_id)
    application.delete()

    return redirect(url_for("applications.index"))
