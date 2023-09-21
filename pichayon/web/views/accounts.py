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
from pichayon.web.client.pichayon_client import pichayon_client

from .. import oauth2
from .. import forms

module = Blueprint("accounts", __name__)


def get_user_and_remember():
    client = oauth2.oauth2_client
    result = client.principal.get("me")
    # print('got: ', result.json())
    data = result.json()

    user = models.User.objects(username=data.get("username", "")).first()
    if not user:
        user = models.User(
            id=data.get("id"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            username=data.get("username"),
            status="active",
        )
        roles = []
        for role in ["student", "lecturer", "staff"]:
            if role in data.get("roles", []):
                roles.append(role)

        user.save()

    if user:
        login_user(user, remember=True)


@module.route("/login", methods=("GET", "POST"))
def login():
    if current_user.is_authenticated:
        if not current_user.gave_informations:
            return redirect(url_for("accounts.edit_profile"))
        return redirect(url_for("dashboard.index"))

    return render_template("/accounts/login.html")


@module.route("/login-engpsu")
def login_engpsu():
    client = oauth2.oauth2_client
    scheme = request.environ.get("HTTP_X_FORWARDED_PROTO", "http")
    redirect_uri = url_for("accounts.authorized_engpsu", _external=True, _scheme=scheme)
    response = client.engpsu.authorize_redirect(redirect_uri)
    return response


@module.route("/authorized-engpsu")
def authorized_engpsu():
    client = oauth2.oauth2_client
    try:
        token = client.engpsu.authorize_access_token()
    except Exception as e:
        print(e)
        return redirect(url_for("accounts.login"))

    userinfo_response = client.engpsu.get("userinfo")
    userinfo = userinfo_response.json()
    # print(userinfo)
    user = models.User.objects(username=userinfo.get("username")).first()

    if not user:
        user = models.User(
            username=userinfo.get("username"),
            system_id=userinfo.get("username"),
            email=userinfo.get("email"),
            first_name=userinfo.get("first_name"),
            last_name=userinfo.get("last_name"),
            status="active",
        )
        user.resources[client.engpsu.name] = userinfo
        # if 'staff_id' in userinfo.keys():
        #     user.roles.append('staff')
        # elif 'student_id' in userinfo.keys():
        #     user.roles.append('student')
        if userinfo["username"].isdigit():
            user.roles.append("student")
        else:
            user.roles.append("supervisor")
            user.gave_informations = True
            user.system_id = userinfo.get("staff_id", user.system_id)

        user.save()

    login_user(user)

    oauth2token = models.OAuth2Token(
        name=client.engpsu.name,
        user=user,
        access_token=token.get("access_token"),
        token_type=token.get("token_type"),
        refresh_token=token.get("refresh_token", None),
        expires=datetime.datetime.fromtimestamp(token.get("expires_in")),
    )
    oauth2token.save()

    return redirect(url_for("dashboard.index"))


@module.route("/logout")
@login_required
def logout():
    logout_user()

    return redirect(url_for("site.index"))


@module.route("/accounts")
@login_required
def index():
    user = current_user
    if request.args.get("user"):
        user_id = request.args.get("user")
        user = models.User.objects.get(id=user_id)
    return render_template("/accounts/index.html", user=user)


@module.route("/accounts/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = forms.accounts.AccountForm(
        obj=current_user,
    )
    if not form.validate_on_submit():
        return render_template("/accounts/edit-profile.html", form=form)

    user = current_user._get_current_object()
    user.first_name = form.first_name.data
    user.last_name = form.last_name.data
    user.first_name_th = form.first_name_th.data
    user.last_name_th = form.last_name_th.data
    user.id_card_number = form.id_card_number.data
    if not user.gave_informations:
        user.gave_informations = True
    user.save()

    return redirect(url_for("accounts.index"))


@module.route(
    "/accounts/identities/add", methods=["GET", "POST"], defaults={"index": -1}
)
@module.route("/accounts/identities/<int:index>/edit", methods=["GET", "POST"])
@login_required
def add_or_edit_identity(index):
    user = current_user

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
    identity.added_by = current_user.id

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

    return redirect(url_for("accounts.index"))
