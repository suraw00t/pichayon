
from . import schemas
import marshmallow_jsonapi as mja


class Error:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Resource:
    def __init__(self, **kwargs):
        self.errors = []
        self.response = kwargs.pop('response', {})

        if 'error' in kwargs:
            kws = kwargs.pop('error')
            self.update_error(**kws)

        if 'errors' in kwargs:
            kws = kwargs.pop('errors')
            self.update_errors(kws)

        self.data = {k.replace('_', '-'): v for k, v in kwargs.items()}

        # if 'id' not in self.data:
        #     self.data['id'] = None

    @property
    def is_error(self):
        if len(self.errors):
            return True

        return False

    def update_error(self, **kwargs):
        self.errors.append(Error(**kwargs))

    def update_errors(self, errors):
        for kwe in errors:
            self.update_error(**kwe)

    def __setattr__(self, name, value):
        if name in ['data', 'errors', 'response']:
            self.__dict__[name] = value
        else:
            if '_' in name:
                name = name.replace('_', '-')
            self.data[name] = value

    def __getattr__(self, name):
        nname = name.replace('_', '-')

        if nname in self.data:
            return self.data[nname]

        if name in self.__dict__:
            return self.__dict__[name]

        raise AttributeError(name)

    def get(self):
        # set_loaded() first ... so if we have to bail, we know we tried.
        self.set_loaded(True)
        if not hasattr(self.manager, 'get'):
            return

        new = self.manager.get(self.id)
        if new:
            # print("new._info:", new._info)
            self._add_details(new._info)
            for (k, v) in new._info.items():
                self._info[k] = v

    def is_loaded(self):
        return self._loaded

    def set_loaded(self, val):
        self._loaded = val


class BaseManager:
    __resource_class__ = None
    __resource_url__ = None

    def __init__(self, api, schema=None, json_schema=None):
        self.api = api

        self.schema = schema
        self.json_schema = json_schema
        if self.json_schema:
            self.schema = schemas.ResourceSchemaFactory.create_schema(
                    self.__resource_class__.__resource_name__,
                    json_schema)

        self.call_method = dict(
                GET=self.api.http_client.get,
                POST=self.api.http_client.post,
                DELETE=self.api.http_client.delete,
                PUT=self.api.http_client.put,
                )

    def get_resource_class(self):
        return self.__resource_class__

    def get_data(self, resource):
        return resource

    def call(self, url, http_method='GET', data=None, schema=None,
             schema_many=False, params=None):
        method = self.call_method.get(http_method, None)
        if method is None:
            return

        response, status_code = method(url, data=data, params=params)
        # print('response', response)
        resource_data = None

        load_schema = self.schema.load
        if schema:
            load_schema = schema.load
       
        if schema_many:
            resource_data = load_schema(response, many=True)
        else:
            resource_data = load_schema(response)

        errors = []

        if 'errors' in response:
            errors = response['errors']

        return resource_data, errors, response

    def _list(self, url=None, params={}):
        url = self.resource_url(url)
        resource_data, errors, response = self.call(url,
                                                    http_method='GET',
                                                    schema_many=True,
                                                    params=params)
        # print('===>',resource_data)
        response_list = [self.__resource_class__(errors=errors,
                                                 response=data,
                                                 **data)
                         for data in resource_data]
        return response_list

    def _get(self, resource_id, url=None, params={}):
        url = self.resource_url(url, resource_id=resource_id)
        resource_data, errors, response = self.call(url,
                                                    http_method='GET',
                                                    params=params)
        return self.__resource_class__(errors=errors,
                                       response=response,
                                       **resource_data)

    def _delete(self, resource_id, url=None, params={}):
        url = self.resource_url(url,
                                resource_id=resource_id)
        # print('response', response)
        resource_data, errors, response = self.call(url,
                                                    http_method='DELETE',
                                                    params=params)

        return response

    def _create(self, resource, url=None, params={}):
        url = self.resource_url(url)
        # print('reso', resource.data)
        # print('===>',
        #        self.schema.fields['building']._Relationship__schema.__dict__)
        data = self.preprocess_data(resource)
        # print('data', data)

        resource_data, errors, response = self.call(
                url,
                http_method='POST',
                data=data,
                params=params)

        return self.__resource_class__(errors=errors,
                                       response=response,
                                       **resource_data)

    def _update(self, resource, url=None, params={}):
        url = self.resource_url(url, resource_id=resource.id)
        data = self.preprocess_data(resource)

        resource_data, errors, response = self.call(
                url,
                http_method='PUT',
                data=data,
                params=params)

        return self.__resource_class__(errors=errors,
                                       response=response,
                                       **resource_data)

    def preprocess_data(self, resource, schema=None):
        data = {}

        if schema:
            data = schema.dump(resource)
        else:
            data = self.schema.dump(resource)

        for name, field in self.schema.fields.items():
            if isinstance(field, mja.fields.Relationship):
                if name not in data:
                    # print('xxx>', resource.data)
                    if name in resource.data:
                        if 'relationships' not in data['data']:
                            data['data']['relationships'] = {}
                        data['data']['relationships'][name] = \
                            field._Relationship__schema.dump(
                                resource.data[name])
        return data

    def resource_url(self, url, resource_id=None):
        url = url if url else self.__resource_url__
        if resource_id:
            url = url + '/' + str(resource_id)
        # if url[-1] != '/':
        #     url = url + '/'

        return url


class Manager(BaseManager):

    def list(self):
        return self._list()

    def create(self, **kwargs):
        resource = self.__resource_class__(**kwargs)
        return super()._create(resource)

    def get(self, resource_id):
        return super()._get(resource_id)

    def update(self, resource):
        return super()._update(resource)

    def delete(self, resource):
        return super()._delete(resource)
