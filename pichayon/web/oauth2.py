from flask import session, redirect, url_for, current_app
from flask_login import current_user, login_user
from authlib.integrations.flask_client import OAuth

# import loginpass

from .. import models
import mongoengine as me

import datetime


def fetch_token(name):
    token = models.OAuth2Token.objects(
        name=name, user=current_user._get_current_object()
    ).first()
    return token.to_dict()


def update_token(name, token):
    item = models.OAuth2Token(
        name=name, user=current_user._get_current_object()
    ).first()
    item.token_type = token.get("token_type", "Bearer")
    item.access_token = token.get("access_token")
    item.refresh_token = token.get("refresh_token")
    item.expires = datetime.datetime.utcfromtimestamp(token.get("expires_at"))
    item.save()
    return item


oauth2_client = OAuth()


def create_user_google(user_info):
    user = models.User(
        username=user_info.get("email"),
        picture_url=user_info.get("picture"),
        email=user_info.get("email"),
        first_name=user_info.get("given_name"),
        last_name=user_info.get("family_name"),
        status="active",
    )
    user.save()
    return user


def create_user_facebook(user_info):
    user = models.User(
        username=user_info.get("email"),
        picture_url=f"http://graph.facebook.com/{user_info.get('sub')}/picture?type=large",
        email=user_info.get("email"),
        first_name=user_info.get("first_name"),
        last_name=user_info.get("last_name"),
        status="active",
    )
    user.save()
    return user


def get_user_info(remote, token):
    if remote.name == "google":
        return token["userinfo"]
    elif remote.name == "facebook":
        USERINFO_FIELDS = [
            "id",
            "name",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "website",
            "gender",
            "locale",
        ]
        USERINFO_ENDPOINT = "me?fields=" + ",".join(USERINFO_FIELDS)
        resp = remote.get(USERINFO_ENDPOINT)
        profile = resp.json()
        return profile


def handle_authorized_oauth2(remote, token):
    user_info = get_user_info(remote, token)

    user = models.User.objects(me.Q(email=user_info.get("email"))).first()
    if not user:
        if remote.name == "google":
            user = create_user_google(user_info)
        elif remote.name == "facebook":
            user = create_user_facebook(user_info)

    login_user(user)

    if token:
        oauth2token = models.OAuth2Token(
            name=remote.name,
            user=user,
            access_token=token.get("access_token"),
            token_type=token.get("token_type"),
            refresh_token=token.get("refresh_token", None),
            expires=datetime.datetime.utcfromtimestamp(token.get("expires_in")),
        )
        oauth2token.save()

    next_uri = session.get("next", None)
    if next_uri:
        session.pop("next")
        return redirect(next_uri)
    return redirect(url_for("site.index"))


def init_oauth(app):
    oauth2_client.init_app(app, fetch_token=fetch_token, update_token=update_token)
    oauth2_client.register(
        name="google",
        server_metadata_url=app.config.get("GOOGLE_METADATA_URL"),
    )
    oauth2_client.register(
        name="facebook",
    )
