import requests
import json
import logging

from .common import base
from .common import http_client

from . import users
from . import rooms
from . import groups

from pichayon.api import schemas

logger = logging.getLogger(__name__)


class Client:
    def __init__(self,
                 api_base_url,
                 access_token=None,
                 json_schemas=None):

        self.api_base_url = api_base_url
        self.access_token = access_token

        self.http_client = http_client.PichayonHTTPClient(
                api_base_url,
                access_token
                )

        self.json_schemas = json_schemas

        if not self.json_schemas:
            self.json_schemas = self.get_json_schemas()

        retrieve_schema = lambda m:\
            self.schemas['definitions'].get(m.__resource_class__.__resource_name__,
                             None)
        # self.users = users.UserManager(self,
        #         json_schema=retrieve_schema(users.UserManager))
        # self.rooms = rooms.RoomManager(self,
        #         json_schema=retrieve_schema(rooms.RoomManager))

        self.users = users.UserManager(self,
                schema=schemas.UserSchema())
        self.groups = groups.GroupManager(self,
                schema=schemas.GroupSchema())

    def authenticate(self, oauth2_token):
        data=dict(
            auth=dict(
                identity=dict(
                    methods=['oauth2_token'],
                    token=dict(
                        provider='principal',
                        token=oauth2_token
                        )
                    )
                )
            )

        response, errors = self.http_client.post('/auth', data=data)

        resource = base.Resource(**response)
        if not resource.is_error:
            self.access_token = resource.access_token
            self.http_client.access_token = self.access_token

        return resource

    def refresh_token(self):
        data = {}
        response, errors = self.http_client.post('/auth/refresh_token',
                                                 data=data)

        resource = base.Resource(**response)
        if not resource.is_error:
            self.access_token = resource.access_token
            self.http_client.access_token = self.access_token

        return resource

    def get_json_schemas(self):
        response, status_code = self.http_client.get('/schemas')
        return response
