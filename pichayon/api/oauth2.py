from flask import current_app
from authlib.flask.client import OAuth


def get_oauth2_client(token):
    oauth2_client = OAuth()

    def fetch_token(name): return token

    oauth2_client.init_app(current_app, fetch_token=fetch_token)
    oauth2_client.register('principal')

    return oauth2_client
