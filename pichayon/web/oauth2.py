from flask import redirect, url_for, current_app
from flask_login import current_user, login_user
from authlib.integrations.flask_client import OAuth
from flask_principal import identity_changed, Identity
import loginpass

from pichayon import models
import mongoengine as me

import datetime


def fetch_token(name):
    token = models.OAuth2Token.objects(
            name=name,
            user=current_user._get_current_object()).first()
    return token.to_dict()


def update_token(name, token):
    item = models.OAuth2Token(
            name=name, user=current_user._get_current_object()).first()
    item.token_type = token.get('token_type', 'Bearer')
    item.access_token = token.get('access_token')
    item.refresh_token = token.get('refresh_token')
    item.expires = datetime.datetime.utcfromtimestamp(token.get('expires_at'))

    item.save()
    return item


oauth2_client = OAuth()


def handle_authorize(remote, token, user_info):

    if not user_info:
        return redirect(url_for('accounts.login'))

    user = models.User.objects(
            me.Q(username=user_info.get('name')) |
            me.Q(email=user_info.get('email'))
            ).first()
    if not user:
        user = models.User(
            username=user_info.get('name'),
            email=user_info.get('email'),
            first_name=user_info.get('given_name'),
            last_name=user_info.get('family_name'),
            status='active')
        user.resources[remote.name] = user_info
        email = user_info.get('email')
        check_id = email[:email.find('@')]
        if check_id.isdigit():
            user.roles.append('student')
            user.system_id = check_id

        user.save()

    login_user(user)
    identity_changed.send(
            current_app._get_current_object(),
            identity=Identity(str(user.id)))


    if token:
        oauth2token = models.OAuth2Token(
                name=remote.name,
                user=user,
                access_token=token.get('access_token'),
                token_type=token.get('token_type'),
                refresh_token=token.get('refresh_token', None),
                expires=datetime.datetime.utcfromtimestamp(
                        token.get('expires_in'))
                )
        oauth2token.save()

    return redirect(url_for('dashboard.index'))


def init_oauth(app):
    oauth2_client.init_app(app,
                           fetch_token=fetch_token,
                           update_token=update_token)
    oauth2_client.register('engpsu')
    # oauth2_client.register('google')
    backends = [loginpass.Google]

    # bp = loginpass.create_flask_blueprint(
    #         backends,
    #         oauth2_client,
    #         handle_authorize)
    # app.register_blueprint(bp)
