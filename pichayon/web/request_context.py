import datetime
from dateutil.parser import parse as dateparse

from flask import g, current_app, session
from flask_login import current_user

from pichayon.client import Client


def init_request_context(app):
    # @app.before_request
    # def init_pichayon_client():
    #     if g.get('pichayon_client', None):
    #         return None

    #     access_token = None
    #     expiry_date = None

    #     user = current_user

    #     if user.is_authenticated:
    #         access_token = user.token.get('access-token', None)
    #         expiry_date = dateparse(user.token.get('expires-date'))

    #     schemas = app.config.get('PICHAYON_SCHEMAS', None)
    #     host = app.config.get('PICHAYON_API')
    #     port = app.config.get('PICHAYON_PORT')
    #     secure = app.config.get('PICHAYON_SECURE')

    #     now = datetime.datetime.utcnow()
    #     if expires_date and now > expires_date:
    #         refresh_token()
    #         access_token = user.token['access-token']

    #     g.pichayon_client = Client(host=host,
    #                                port=port,
    #                                secure_connection=secure,
    #                                access_token=access_token,
    #                                schemas=schemas)

    #     if not schemas:
    #         app.config['PICHAYON_SCHEMAS'] = g.pichayon_client.schemas

    @app.before_request
    def init_application_client():
        g.get_pichayon_client = get_pichayon_client


def get_pichayon_client():

    user = current_user
    app = current_app

    json_schemas = app.config.get('PICHAYON_SCHEMAS', None)
    pichayon_api_base_url = app.config.get('PICHAYON_API_BASE_URL')

    if not user.is_authenticated:
        return Client(api_base_url=pichayon_api_base_url,
                      json_schemas=json_schemas)

    access_token = user.token.get('access-token', None)
    expires_at = datetime.datetime.utcfromtimestamp(
            user.token.get('expires-at', 0))

    json_schemas = app.config.get('PICHAYON_SCHEMAS', {})

    now = datetime.datetime.utcnow()
    if now > expires_at:
        refresh_token()
        access_token = user.token.get('access-token', None)

    return Client(api_base_url=pichayon_api_base_url,
                  access_token=access_token,
                  json_schemas=json_schemas)


def refresh_token():
    app = current_app
    user = current_user

    schemas = app.config.get('PICHAYON_SCHEMAS', None)
    host = app.config.get('PICHAYON_HOST')
    port = app.config.get('PICHAYON_PORT')
    secure = app.config.get('PICHAYON_SECURE')
    refresh_token = user.token.get('refresh-token', None)

    if not refresh_token:
        raise Exception()

    client = Client(host=host,
                    port=port,
                    secure_connection=secure,
                    access_token=refresh_token,
                    schemas=schemas)

    resource = client.refresh_token()
    user.token.update(resource.data)
    session['token'] = resource.data
