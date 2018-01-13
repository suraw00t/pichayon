import requests
import json
import logging

from .common import base
from .common import http_client

from . import users

logger = logging.getLogger(__name__)


class Client:
    def __init__(self,
                 oauth2_access_token=None,
                 host='127.0.0.1',
                 port=80,
                 secure_connection=False,
                 access_token=None,
                 schemas=None):

        self.oauth2_access_token = oauth2_access_token
        self.host = host
        self.port = port
        self.secure_connection = secure_connection
        self.access_token = access_token

        self.http_client = http_client.HHServiceHTTPClient(
                oauth2_access_token,
                host,
                port,
                secure_connection,
                access_token
                )

        self.schemas = schemas
        if not self.schemas:
            self.schemas = self.get_schemas()

        
        retrieve_schema = lambda m:\
            self.schemas.get(m.__resource_class__.__resource_name__,
                             None)
        self.users = users.UserManager(self,
                schema=retrieve_schema(users.UserManager))
        # self.buildings = buildings.BuildingManager(self,
        #         schema=retrieve_schema(buildings.BuildingManager))
        # self.applications = applications.ApplicationManager(self,
        #         schema=retrieve_schema(applications.ApplicationManager))
   
    def authenticate(self, name=None, password=None):
        if name:
            self.name = name
            self.http_client.name = name
        if password:
            self.password = password
            self.http_client.password = password

        data=dict(
            auth=dict(
                identity=dict(
                    methods=['password'],
                    password=dict(
                        user=dict(
                            name=self.name,
                            password=self.password
                        )
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

    def get_schemas(self):
        response, status_code = self.http_client.get('/schemas')
        return response
