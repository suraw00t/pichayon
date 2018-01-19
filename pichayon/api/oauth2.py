from flask import session
from authlib.flask.client import OAuth

from . import models

oauth2_client = OAuth()


def fetch_token(name):
    token = session.pop(name)
    return token


def init_oauth2(app):
    oauth2_client.init_app(app, fetch_token=fetch_token)
    oauth2_client.register('principal')
