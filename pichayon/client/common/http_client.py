import requests
import json
import logging

logger = logging.getLogger(__name__)


class HTTPClient:
    def __init__(self,
                 api_base_url,
                 access_token=None):

        self.api_base_url = api_base_url
        self.access_token = access_token
        self.session = requests.session()


    def request(self, url, method, **kwargs):
        kwargs['headers']['Content-Type'] = 'application/vnd.api+json'

        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])

        # print('{}: {}\nargs => {}'.format(method, url, str(kwargs)))
        logger.debug(method + url + '\nargs:' + str(kwargs))
        response = self.session.request(method, 
                                    url,
                                    **kwargs)

        logger.debug('response => code: {} data: {}'\
                .format(response.status_code, response.json()))
        # print('response => code: {} data: {}'\
        #        .format(response.status_code, response.json()))

        return response.json(), response.status_code


    def _cs_request(self, url, method, **kwargs):
        kwargs.setdefault('headers', {})
        if self.access_token:
            kwargs['headers']['Authorization'] = 'Bearer {}'.format(self.access_token)

        request_url = self.api_base_url 
        if self.api_base_url[-1] == '/' and url[0] == '/':
            request_url = self.api_base_url[:-1] + url
        else:
            request_url = self.api_base_url + url

        return self.request(request_url, 
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


class PichayonHTTPClient(HTTPClient):
    def __init__(self,
                 api_base_url,
                 access_token=None):

        self.api_base_url = api_base_url
        self.access_token = access_token
        self.user_id = None

        super().__init__(self.api_base_url, access_token)
