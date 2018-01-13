import datetime
from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect,
                   session,
                   request)

from flask_login import (login_user,
                         logout_user,
                         login_required,
                         current_user)

from pichayon.web import oauth2, acl

module = Blueprint('web.accounts', __name__)

cache = dict()


def get_user_and_remember(token):
    client = oauth2.oauth2_client
    result = client.principal.get('profile')
    print('got: ', result.json())
    profile = result.json()

    user = acl.User(profile=profile, token=token)

    login_user(user)


@module.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    return render_template('/accounts/login.html')


@module.route('/login-principal')
def login_principal():
    client = oauth2.oauth2_client
    callback = url_for('web.accounts.authorized_principal',
                       _external=True)
    response = client.principal.authorize_redirect(callback)

    cache[session['_principal_state_']] = dict(session)
    return response


@module.route('/authorized-principal')
def authorized_principal():
    if request.args.get('state') in cache:
        sdata = cache.pop(request.args.get('state'))
        session.update(sdata)

    client = oauth2.oauth2_client

    try:
        token = client.principal.authorize_access_token()
    except Exception as e:
        print(e)
        return redirect(url_for('web.accounts.login'))

    get_user_and_remember(token)
    return redirect(url_for('web.dashboard.index'))


@module.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('web.site.index'))
