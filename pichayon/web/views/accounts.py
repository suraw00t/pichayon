import datetime

from flask import (Blueprint,
                   current_app,
                   render_template,
                   url_for,
                   redirect,
                   request,
                   session,
                   )

from flask_login import login_user, logout_user, login_required, current_user
from flask_principal import identity_changed, Identity, AnonymousIdentity
from pichayon import models
from .. import oauth2
from .. import forms

module = Blueprint('accounts', __name__)


def get_user_and_remember():
    client = oauth2.oauth2_client
    result = client.principal.get('me')
    # print('got: ', result.json())
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

    if user:
        login_user(user, remember=True)


@module.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        if not current_user.gave_informations:
            return redirect(url_for('accounts.edit_profile'))
        return redirect(url_for('dashboard.index'))

    return render_template('/accounts/login.html')


# @module.route('/login-principal')
# def login_principal():
#     client = oauth2.oauth2_client
#     redirect_uri = url_for('accounts.authorized_principal',
#                            _external=True)
#     response = client.principal.authorize_redirect(redirect_uri)

#     return response


@module.route('/login-engpsu')
def login_engpsu():
    client = oauth2.oauth2_client
    redirect_uri = url_for('accounts.authorized_engpsu',
                           _external=True)
    response = client.engpsu.authorize_redirect(redirect_uri)
    return response

# @module.route('/authorized-principal')
# def authorized_principal():
#     client = oauth2.oauth2_client

#     try:
#         token = client.principal.authorize_access_token()
#     except Exception as e:
#         print(e)
#         return redirect(url_for('accounts.login'))

#     get_user_and_remember()
#     oauth2token = models.OAuth2Token(
#             name=client.principal.name,
#             user=current_user._get_current_object(),
#             access_token=token.get('access_token'),
#             token_type=token.get('token_type'),
#             refresh_token=token.get('refresh_token', None),
#             expires=datetime.datetime.utcfromtimestamp(
#                 token.get('expires_at'))
#             )
#     oauth2token.save()

#     return redirect(url_for('dashboard.index'))


@module.route('/authorized-engpsu')
def authorized_engpsu():
    client = oauth2.oauth2_client
    try:
        token = client.engpsu.authorize_access_token()
    except Exception as e:
        print(e)
        return redirect(url_for('accounts.login'))

    userinfo_response = client.engpsu.get('userinfo')
    userinfo = userinfo_response.json()
    # print(userinfo)
    user = models.User.objects(username=userinfo.get('username')).first()

    if not user:
        user = models.User(
                username=userinfo.get('username'),
                system_id=userinfo.get('username'),
                email=userinfo.get('email'),
                first_name=userinfo.get('first_name'),
                last_name=userinfo.get('last_name'),
                status='active')
        user.resources[client.engpsu.name] = userinfo
        # if 'staff_id' in userinfo.keys():
        #     user.roles.append('staff')
        # elif 'student_id' in userinfo.keys():
        #     user.roles.append('student')
        if userinfo['username'].isdigit():
            user.roles.append('student')
        else:
            user.roles.append('supervisor')
            user.gave_informations = True
            user.system_id = userinfo.get('staff_id', user.system_id)

        user.save()

    login_user(user)
    identity_changed.send(
            current_app._get_current_object(),
            identity=Identity(str(user.id)))

    oauth2token = models.OAuth2Token(
            name=client.engpsu.name,
            user=user,
            access_token=token.get('access_token'),
            token_type=token.get('token_type'),
            refresh_token=token.get('refresh_token', None),
            expires=datetime.datetime.fromtimestamp(
                token.get('expires_in'))
            )
    oauth2token.save()

    return redirect(url_for('dashboard.index'))


@module.route('/logout')
@login_required
def logout():
    logout_user()
	
	# Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    return redirect(url_for('site.index'))


@module.route('/accounts')
@login_required
def index():
    user = current_user
    if request.args.get('user'):
        user_id = request.args.get('user')
        user = models.User.objects.get(id=user_id)
    return render_template('/accounts/index.html',
                           user=user)


@module.route('/accounts/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = forms.accounts.AccountForm(
            obj=current_user,
            )
    if not form.validate_on_submit():
        return render_template('/accounts/edit-profile.html', form=form)

    user = current_user._get_current_object()
    user.first_name = form.first_name.data
    user.last_name = form.last_name.data
    user.first_name_th = form.first_name_th.data
    user.last_name_th = form.last_name_th.data
    user.id_card_number = form.id_card_number.data
    if not user.gave_informations:
        user.gave_informations = True
    user.save()

    return redirect(url_for('accounts.index'))
