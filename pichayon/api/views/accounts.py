
from pichayon.api import models
from pichayon.api import oauth2


def get_principal_user(oauth2_token):
    print('in get_principal_user')
    client = oauth2.get_oauth2_client(oauth2_token)
    # client = oauth2.oauth2_client
    result = client.principal.get('email')
    data = result.json()

    user = models.User.objects(
            id=data.get('id', '')).first()

    if not user:
        result = client.principal.get('profile')
        data = result.json()

        user = models.User(id=data.get('id'),
                           first_name=data.get('first_name'),
                           last_name=data.get('last_name'),
                           email=data.get('email'),
                           username=data.get('username'),
                           status='active')
        for role in ['student', 'lecturer', 'staff', 'admin']:
            if role in data.get('roles', []):
                user.roles.append(role)

        user.save()

    return user
