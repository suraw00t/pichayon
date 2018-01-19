
import datetime

from flask import (Blueprint,
                   request,
                   session,
                   abort,
                   current_app)

from pichayon.api.renderers import render_json
from pichayon.api import models

import mongoengine as me
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                current_user,
                                jwt_refresh_token_required,
                                )
from flask_jwt_extended.utils import decode_token

from .. import accounts

module = Blueprint('auth', __name__, url_prefix='/auth')


@module.route('', methods=['post'])
def auth():
    auth_dict = request.get_json()['auth']

    try:
        provider = auth_dict['identity']['token']['provider']
        token = auth_dict['identity']['token']['token']
        session[provider] = token
    except Exception as e:
        response_dict = request.get_json()
        response_dict.update(e.messages)
        response = render_json(response_dict)
        response.status_code = 400
        abort(response)

    user = accounts.get_principal_user()

    if user:
        app = current_app
        now = datetime.datetime.utcnow()
        expires_at = now + app.config.get('JWT_ACCESS_TOKEN_EXPIRES')

        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)

        token = dict(
            methods=['jwt_token'],
            user=dict(
                id=user.id,
                name=user.username
                ),
            access_token=access_token,
            refresh_token=refresh_token,
            issued_date=datetime.datetime.utcnow(),
            expires_at=expires_at
            )
        return render_json(token)

    errors = [
        {
          'status': '401',
          'title':  'User or Password mismatch',
          'detail': 'User or Password mismatch'
        }
    ]

    response_dict = request.get_json()
    response_dict['errors'] = errors

    response = render_json(response_dict)
    response.status_code = 401
    abort(response)


@module.route('/refresh_token', methods=['POST'])
@jwt_refresh_token_required
def refresh_token():
    user = current_user

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    jwt_data = decode_token(access_token)

    token = dict(
        access_token=access_token,
        refresh_token=refresh_token,
        issued_date=datetime.datetime.utcnow(),
        expiry_date=datetime.datetime.utcfromtimestamp(
            jwt_data.get('exp'))
        )

    return render_json(token)
