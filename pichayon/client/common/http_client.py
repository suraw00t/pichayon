import requests
import json
import logging

logger = logging.getLogger(__name__)


class HTTPClient:
    def __init__(self,
                 api_url,
                 access_token=None):

        self.api_url = api_url
        self.access_token = access_token
        self.session = requests.session()


    def request(self, url, method, **kwargs):
        kwargs['headers']['Content-Type'] = 'application/vnd.api+json'

        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])

        logger.debug(method + url + '\nargs:' + str(kwargs))
        response = self.session.request(method, 
                                    url,
                                    **kwargs)

        logger.debug('response => code: {} data: {}'\
                .format(response.status_code, response.json()))

        return response.json(), response.status_code


    def _cs_request(self, url, method, **kwargs):
        kwargs.setdefault('headers', {})
        if self.access_token:
            kwargs['headers']['Authorization'] = 'Bearer {}'.format(self.access_token)

        return self.request(self.api_url + url, 
                            method,
                            **kwargs)

    def get(self, url, **kwargs):
        return self._cs_request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        return self._cs_request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        return self._cs_request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        return self._cs_request(url, 'DELETE', **kwargs)


class HHServiceHTTPClient(HTTPClient):
    def __init__(self,
                 name=None,
                 password=None,
                 host='127.0.0.1',
                 port=8080,
                 secure_connection=False,
                 access_token=None):

        self.name = name
        self.password = password
        self.host = host
        self.port = port
        self.secure_connection = secure_connection
        self.access_token = access_token
        self.user_id = None

        self.scheme = 'http'
        if self.secure_connection:
            self.scheme = 'https'

        self.api_url = '%s://%s:%d' % (self.scheme, self.host, self.port)

        super().__init__(self.api_url, access_token)
