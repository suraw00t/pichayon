import datetime
import urllib

from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect,
                   session,
                   request)

from pichayon.api import models
from pichayon.api import oauth2

module = Blueprint('api.accounts', __name__)

cache = dict()


def get_user():
    client = oauth2.oauth2_client
    result = client.principal.get('me')
    print('got: ', result.json())
    data = result.json()

    user = models.User.objects(
            username=data.get('username', '')).first()
    if not user:
        user = models.User(id=data.get('id'),
                           first_name=data.get('first_name'),
                           last_name=data.get('last_name'),
                           email=data.get('email'),
                           username=data.get('username'),
                           status='active')
        roles = []
        for role in ['student', 'lecturer', 'staff']:
            if role in data.get('roles', []):
                roles.append(role)

        user.save()

    return user
    

@module.route('/login-principal', methods=['POST'])
def login_principal():
    client = oauth2.oauth2_client
    return 'xxx'

    # callback = url_for('api.accounts.authorized_principal',
    #                    _external=True)
    # response = client.principal.authorize_redirect(callback)

    # cache[session['_principal_state_']] = dict(session)
    # cache[session['_principal_state_']]['redirect_uri'] = \
    #     request.args.get('redirect_uri', None)
    # return response


@module.route('/authorized-principal')
def authorized_principal():
    redirect_uri = None
    if request.args.get('state') in cache:
        sdata = cache.pop(request.args.get('state'))
        session.update(sdata)
        redirect_uri = sdata.get('redirect_uri', None)

    client = oauth2.oauth2_client

    token = client.principal.authorize_access_token()

    user = get_user()
    oauth2token = models.OAuth2Token(
            name=client.principal.name,
            user=current_user._get_current_object(),
            access_token=token.get('access_token'),
            token_type=token.get('token_type'),
            refresh_token=token.get('refresh_token', None),
            expires=datetime.datetime.utcfromtimestamp(
                token.get('expires_at'))
            )
    oauth2token.save()

    if redirect_uri:
        auth_code = models.AuthCode(user=user,
                expires_date=datetime.datetime.utcnow() +
                datetime.timedelta(minutes=1))
        auth_code.save()

        query = urllib.parse.urlencode({
            'code': str(auth_code.id)})
        url = '{}?{}'.format(redirect_uri, query)
        return redirect(url)
    
    return 'Can not redirect'


