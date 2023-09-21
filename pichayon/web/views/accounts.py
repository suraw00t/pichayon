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
        return redirect(url_for("dashboard.index"))

    if "next" in request.args:
        session["next"] = request.args.get("next", None)
    return render_template("/accounts/login.html")


@module.route("/login/<name>")
def login_oauth(name):
    client = oauth2.oauth2_client

    scheme = request.environ.get("HTTP_X_FORWARDED_PROTO", "http")
    redirect_uri = url_for(
        "accounts.authorized_oauth", name=name, _external=True, _scheme=scheme
    )
    response = None
    if name == "google":
        response = client.google.authorize_redirect(redirect_uri)
    elif name == "facebook":
        response = client.facebook.authorize_redirect(redirect_uri)
    elif name == "line":
        response = client.line.authorize_redirect(redirect_uri)

    elif name == "psu":
        response = client.psu.authorize_redirect(redirect_uri)
    elif name == "engpsu":
        response = client.engpsu.authorize_redirect(redirect_uri)
    return response


@module.route("/auth/<name>")
def authorized_oauth(name):
    client = oauth2.oauth2_client
    remote = None
    try:
        if name == "google":
            remote = client.google
        elif name == "facebook":
            remote = client.facebook
        elif name == "line":
            remote = client.line
        elif name == "psu":
            remote = client.psu
        elif name == "engpsu":
            remote = client.engpsu

        token = remote.authorize_access_token()

    except Exception as e:
        print("autorize access error =>", e)
        return redirect(url_for("accounts.login"))

    session["oauth_provider"] = name
    return oauth2.handle_authorized_oauth2(remote, token)


@module.route("/logout")
@login_required
def logout():
    name = session.get("oauth_provider")
    logout_user()
    session.clear()

    client = oauth2.oauth2_client
    remote = None
    logout_url = None
    if name == "google":
        remote = client.google
        logout_url = f"{ remote.server_metadata.get('end_session_endpoint') }?redirect={ request.scheme }://{ request.host }"
    elif name == "facebook":
        remote = client.facebook
    elif name == "line":
        remote = client.line
    elif name == "psu":
        remote = client.psu
        logout_url = f"{ remote.server_metadata.get('end_session_endpoint') }"
    elif name == "engpsu":
        remote = client.engpsu

    if logout_url:
        return redirect(logout_url)

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
    identity.added_with = "web"
    identity.added_by = str(current_user.id)
    identity.updated_date = datetime.datetime.now()

    if index < 0:
        is_found = False
        for idr in user.identities:
            if idr.identifier == form.identifier.data:
                is_found = True
                break
        if not is_found:
            user.identities.append(identity)

    user.save()

    pichayon_client.update_member(user=user)

    return redirect(url_for("accounts.index"))
