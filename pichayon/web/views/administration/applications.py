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
from pichayon.web.client.pichayon_client import pichayon_client
from flask_mongoengine import Pagination


from pichayon import models
from pichayon.web import acl
from pichayon.web import forms

module = Blueprint("applications", __name__, url_prefix="/applications")


@module.route("")
@acl.role_required("admin", "lecturer")
def index():
    applications = models.Application.objects(status="pending").order_by("created_date")
    page = request.args.get("page", default=1, type=int)

    if "admin" not in current_user.roles:
        user = current_user._get_current_object()
        user_group_members = models.UserGroupMember.objects(user=user, role="admin")
        if user_group_members:
            applications.filter(user=user)

            return redirect(url_for("applications.approve"))

    paginated_applications = Pagination(applications, page=page, per_page=30)

    return render_template(
        "/administration/applications/index.html",
        paginated_applications=paginated_applications,
    )


@module.route("/approved")
@acl.role_required("admin", "lecturer")
def approved():
    applications = models.Application.objects(status__ne="pending").order_by(
        "-approved_date"
    )
    page = request.args.get("page", default=1, type=int)

    if "admin" not in current_user.roles:
        user = current_user._get_current_object()
        user_group_members = models.UserGroupMember.objects(user=user, role="admin")
        if user_group_members:
            applications.filter(user=user)

            return redirect(url_for("applications.approve"))

    paginated_applications = Pagination(applications, page=page, per_page=30)

    return render_template(
        "/administration/applications/index.html",
        paginated_applications=paginated_applications,
    )


@module.route("/<application_id>/approve")
@acl.role_required("admin", "lecturer")
def approve(application_id):
    # application = models.Application.objects().get(id=application_id)

    # application.approved_by = current_user._get_current_object()
    # application.approved_date = datetime.datetime.now()
    # application.status = "approved"
    # application.ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)

    # application.save()

    return redirect(
        url_for(
            "administration.applications.add_or_edit_user_to_user_group",
            application_id=application_id,
        )
    )


@module.route(
    "/<application_id>/add-or-edit-user-to-user-group", methods=["GET", "POST"]
)
@acl.role_required("admin", "lecturer")
def add_or_edit_user_to_user_group(application_id):
    application = models.Application.objects().get(id=application_id)
    form = forms.applications.UserGroupMemberFromApplicationForm()

    user_groups = []

    if "admin" in current_user.roles:
        user_groups = models.UserGroup.objects(status="active").order_by("name")
    else:
        admin_group_members = models.UserGroupMember.objects(
            role="admin", user=current_user._get_current_object()
        ).order_by("name")

        user_groups = [
            user_group_member.group for user_group_member in admin_group_members
        ]

    user_group_members = models.UserGroupMember.objects(user=application.user)
    groups_of_user = [ugm.group for ugm in user_group_members]

    form.user_groups.choices = [
        (str(user_group.id), user_group.name)
        for user_group in user_groups
        if user_group not in groups_of_user
    ]

    if request.method == "GET":
        form.started_date.data = application.started_date
        form.expired_date.data = application.ended_date

    if not form.validate_on_submit():
        return render_template(
            "/administration/applications/add-or-edit-user-to-user-group.html",
            form=form,
            application=application,
        )

    for user_group_id in form.user_groups.data:
        user_group = models.UserGroup.objects(id=user_group_id).first()
        if not user_group:
            continue

        user_group_member = models.UserGroupMember.objects(
            user=application.user,
            group=user_group,
        ).first()

        if not user_group_member:
            user_group_member = models.UserGroupMember(
                user=application.user,
                group=user_group,
                started_date=form.started_date.data,
                expired_date=form.expired_date.data,
                added_by=current_user._get_current_object(),
            )

        user_group_member.application = application
        user_group_member.started_date = form.started_date.data
        user_group_member.expired_date = form.expired_date.data
        user_group_member.save()

        application.approved_date = datetime.datetime.now()
        application.status = "approved"
        application.ip_address = request.headers.get(
            "X-Forwarded-For", request.remote_addr
        )

        application.save()

        pichayon_client.update_member(application.user)

    return redirect(url_for("administration.applications.index"))


@module.route("/<application_id>/reject")
@acl.role_required("admin", "lecturer")
def reject(application_id):
    application = models.Application.objects().get(id=application_id)

    application.approved_by = current_user._get_current_object()
    application.approved_date = datetime.datetime.now()
    application.status = "rejected"
    application.ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    application.save()

    return redirect(
        url_for("administration.applications.comment", application_id=application_id)
    )


@module.route("/<application_id>/comment", methods=["GET", "POST"])
@acl.role_required("admin", "lecturer")
def comment(application_id):
    application = models.Application.objects().get(id=application_id)
    form = forms.applications.ApplicationRemarkForm(obj=application)

    if not form.validate_on_submit():
        return render_template(
            "/administration/applications/comment.html",
            form=form,
            application_id=application_id,
        )

    form.populate_obj(application)
    application.user = current_user._get_current_object()

    application.ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    application.save()

    return redirect(
        url_for("administration.applications.index", application_id=application_id)
    )
