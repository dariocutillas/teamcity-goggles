""" 
Implementation of the TeamCity REST end point.

Refer to https://www.jetbrains.com/help/teamcity/rest-api.html#RESTAPI-GeneralUsagePrinciples
for documentation regarding TeamCity REST API.
"""

import os
import re
import requests
import itertools

from collections import namedtuple


""" Determines how connection to the server shall occurr."""
ServerConfig = namedtuple('ServerConfig', 'uri,auth')


_Request = namedtuple('Request', 'uri,headers,params')


""" Represents the authentification mechanism to run queries."""
class Auth:
    Basic = namedtuple('Basic', 'username, password')
    Token = namedtuple('Token', 'token')
    
    """ Internal. Use the factory methods `token` and `basic` instead."""
    def __init__(self, data):
        self._data = data

    """ Returns the result of applying a mapping function depending
        on the the underlying Auth option."""
    def map(self, basic_mapping, token_mapping):
        visitor = {
            Auth.Basic: basic_mapping,
            Auth.Token: token_mapping
        }
        return visitor[type(self._data)](self._data)

    """ Creates an Auth instance for token based authentification."""
    @classmethod
    def token(cls, token):
        return Auth(cls.Token(token))
        
    """ Creates an Auth instance for username/password identification."""
    @classmethod
    def basic(cls, username, password):
        return Auth(cls.Basic(username, password))


class RequestFormatter:
    def __init__(self, server_uri):
        self.server_uri = server_uri

    def build_configurations(self):
        return self._build_types(False)
        
    def build_templates(self):
        return self._build_types(True)
    
    def _build_types(self, template_flag):
        uri = self._format_uri('/app/rest/buildTypes')
        return _Request(uri, {}, {'locator':'templateFlag:{template_flag}'})

    def build_type_parameters(self, href):
        uri = self._format_uri(f"{href}/parameters")
        return _Request(uri, {}, {})
        
    def _format_uri(self, path):
        return f"{self.server_uri}{path}"


class RequestError(Exception):
    pass


class RestClient:
    def __init__(self, auth):
        self.auth = auth

    def request_json(self, request):
        headers = {"Accept": "application/json"}
        response = self._request(request, headers)
        return response.json()

    def _request(self, request, headers):
        def whenToken(auth):
            headers['Authorization'] = f'Bearer {auth.token}'
            return requests.get(uri, headers=headers)
            
        def whenBasic(auth):
            return requests.get(uri, auth=auth, headers=headers)
            
        uri = request.uri
        response = self.auth.map(whenBasic, whenToken)

        if not response:
            raise RequestError(response)

        if 'nextHref' in response:
            raise NotImplementedError('Support for paged responses has not been implemented.')
        
        return response


""" Represents a parameter (property) resource."""
class Parameter:
    def __init__(self, json):
        self.json = json

    @property
    def name(self):
        return self._get('name')

    @property
    def inherited(self):
        return self._get('inherited')

    @property
    def value(self):
        return self._get('value')

    def _get(self, attribute):
        return self.json.get(attribute, None)


""" A build type resource."""
class BuildType:
    def __init__(self, client, json, request_formatter):
        self.client = client
        self.json = json
        self.request_formatter = request_formatter

    """ Fetch parameters."""
    def parameters(self):
        request = self.request_formatter.build_type_parameters(self.json['href'])
        json = self.client.request_json(request)
        for parameter_json in json['property']:
            yield Parameter(parameter_json)

    @property
    def id(self):
        return self.json['id']

    @property
    def name(self):
        return self.json['name']

    @property
    def project_id(self):
        return self.json['projectId']

    @property
    def web_url(self):
        return self.json['webUrl']


""" The TeamCity end-point and access to the api."""
class TeamCityEndPoint:
    """ Creates an instance of a TeamCityClient with a custom Rest client and request 
        formatter. You'd normally want to use the `create` factory method instead.
    """
    def __init__(self, client, request_formatter):
        self.client = client
        self.request_formatter = request_formatter

    """ Fetch build configurations."""
    def build_configurations(self):
        request = self.request_formatter.build_configurations()
        return self._build_types(request)

    """ Fetch build templates."""
    def build_templates(self):
        request = self.request_formatter.build_templates()
        return self._build_types(request)

    def _build_types(self, request):
        json = self.client.request_json(request)
        for _,build_type_json in enumerate(json['buildType']):
            yield BuildType(self.client, build_type_json, self.request_formatter)
        
    @classmethod
    def create(cls, server_config):
        client = RestClient(server_config.auth)
        request_formatter = RequestFormatter(server_config.uri)
        return cls(client, request_formatter)
