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


def get_principal_user():
    client = oauth2.oauth2_client
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
        roles = []
        for role in ['student', 'lecturer', 'staff', 'admin']:
            if role in data.get('roles', []):
                roles.append(role)

        user.save()

    return user
