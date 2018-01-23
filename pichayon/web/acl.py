from flask import redirect, url_for, request, session
from flask_login import LoginManager, UserMixin, current_user, login_url
from flask_allows import Allows


allows = Allows(identity_loader=lambda: current_user)


class User(UserMixin):
    def __init__(self, profile={}, oauth2_token={}, token={}):
        self.token = token
        self.oauth2_token = oauth2_token
        self.profile = profile

        self.roles = []

        for k, v in profile.items():
            k = k.replace('-', '_')
            setattr(self, k, v)

    def to_session_dict(self):
        return dict(profile=self.profile,
                    token=self.token,
                    oauth2_token=self.oauth2_token)

    def has_roles(self, roles=[]):
        for role in roles:
            if role in self.roles:
                return True
        return False


def is_admin(ident, request):
    return 'admin' in ident.roles


def is_developer(ident, request):
    return 'developer' in ident.roles


def is_staff(ident, request):
    return 'staff' in ident.roles


def init_acl(app):
    # initial login manager
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id):
        # user = models.User.objects.with_id(user_id)
        # return user
        if user_id not in session:
            return User()

        return User(profile=session[user_id]['profile'],
                    oauth2_token=session[user_id]['oauth2_token'],
                    token=session[user_id]['token'])

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        if request.method == 'GET':
            response = redirect(login_url('web.accounts.login',
                                          request.url))
            return response

        return redirect(url_for('web.accounts.login'))
