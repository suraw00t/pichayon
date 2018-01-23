from flask import (Blueprint,
                   render_template,
                   url_for,
                   redirect,
                   session,
                   request,
                   g)

from flask_login import (login_user,
                         logout_user,
                         login_required,
                         current_user)

from pichayon.web import oauth2, acl

module = Blueprint('web.accounts', __name__)

cache = dict()


def get_user_and_remember(oauth2_token):

    pichayon_client = g.get_pichayon_client()
    result = pichayon_client.authenticate(oauth2_token)

    pichayon_client.access_token = result.access_token
    user = pichayon_client.users.get(result.user['id'])

    user = acl.User(profile=user.data,
                    oauth2_token=oauth2_token,
                    token=result.data)

    session[user.id] = user.to_session_dict()

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
    print('login cache: ', cache)
    if request.args.get('state') in cache:
        sdata = cache.pop(request.args.get('state'))
        session.update(sdata)

    print('login session:', session)
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
    if current_user.id in session:
        session.pop(current_user.id)
    logout_user()
    return redirect(url_for('web.site.index'))
