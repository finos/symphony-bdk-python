"""
    Authenticator API

    For bots and other on-premise processes to authenticate. Once authenticated, the bot will be able to use the methods described in serviceAPI.yaml and agentAPI.yaml.  Connections to the servers will be over client authenticated TLS, the servers for this API will perform the authentication by inspecting the certificate presented by the SSLSocketClient.  There will be two implementations of this API, one on your Pod and one on the Key Manager. In order to fully authenticate, an API client will have to call both of these implementations and pass both of the session tokens returned as headers in all subsequent requests to the Symphony API.   # noqa: E501

    The version of the OpenAPI document: 20.14.1
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401

from symphony.bdk.gen.api_client import ApiClient, Endpoint as _Endpoint
from symphony.bdk.gen.model_utils import (  # noqa: F401
    check_allowed_values,
    check_validations,
    date,
    datetime,
    file_type,
    none_type,
    validate_and_convert_types
)
from symphony.bdk.gen.auth_model.error import Error
from symphony.bdk.gen.auth_model.extension_app_authenticate_request import ExtensionAppAuthenticateRequest
from symphony.bdk.gen.auth_model.extension_app_tokens import ExtensionAppTokens
from symphony.bdk.gen.auth_model.obo_auth_response import OboAuthResponse
from symphony.bdk.gen.auth_model.success_response import SuccessResponse
from symphony.bdk.gen.auth_model.token import Token


class CertificateAuthenticationApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        self.v1_app_authenticate_post_endpoint = _Endpoint(
            settings={
                'response_type': (Token,),
                'auth': [],
                'endpoint_path': '/v1/app/authenticate',
                'operation_id': 'v1_app_authenticate_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                ],
                'required': [],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                },
                'attribute_map': {
                },
                'location_map': {
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client
        )
        self.v1_app_user_uid_authenticate_post_endpoint = _Endpoint(
            settings={
                'response_type': (OboAuthResponse,),
                'auth': [],
                'endpoint_path': '/v1/app/user/{uid}/authenticate',
                'operation_id': 'v1_app_user_uid_authenticate_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'uid',
                    'session_token',
                ],
                'required': [
                    'uid',
                    'session_token',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'uid':
                        (int,),
                    'session_token':
                        (str,),
                },
                'attribute_map': {
                    'uid': 'uid',
                    'session_token': 'sessionToken',
                },
                'location_map': {
                    'uid': 'path',
                    'session_token': 'header',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client
        )
        self.v1_app_username_username_authenticate_post_endpoint = _Endpoint(
            settings={
                'response_type': (OboAuthResponse,),
                'auth': [],
                'endpoint_path': '/v1/app/username/{username}/authenticate',
                'operation_id': 'v1_app_username_username_authenticate_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'username',
                    'session_token',
                ],
                'required': [
                    'username',
                    'session_token',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'username':
                        (str,),
                    'session_token':
                        (str,),
                },
                'attribute_map': {
                    'username': 'username',
                    'session_token': 'sessionToken',
                },
                'location_map': {
                    'username': 'path',
                    'session_token': 'header',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client
        )
        self.v1_authenticate_extension_app_post_endpoint = _Endpoint(
            settings={
                'response_type': (ExtensionAppTokens,),
                'auth': [],
                'endpoint_path': '/v1/authenticate/extensionApp',
                'operation_id': 'v1_authenticate_extension_app_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'auth_request',
                ],
                'required': [
                    'auth_request',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'auth_request':
                        (ExtensionAppAuthenticateRequest,),
                },
                'attribute_map': {
                },
                'location_map': {
                    'auth_request': 'body',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [
                    'application/json'
                ]
            },
            api_client=api_client
        )
        self.v1_authenticate_post_endpoint = _Endpoint(
            settings={
                'response_type': (Token,),
                'auth': [],
                'endpoint_path': '/v1/authenticate',
                'operation_id': 'v1_authenticate_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                ],
                'required': [],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                },
                'attribute_map': {
                },
                'location_map': {
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client
        )
        self.v1_logout_post_endpoint = _Endpoint(
            settings={
                'response_type': (SuccessResponse,),
                'auth': [],
                'endpoint_path': '/v1/logout',
                'operation_id': 'v1_logout_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'session_token',
                ],
                'required': [
                    'session_token',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'session_token':
                        (str,),
                },
                'attribute_map': {
                    'session_token': 'sessionToken',
                },
                'location_map': {
                    'session_token': 'header',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client
        )

    def v1_app_authenticate_post(
        self,
        **kwargs
    ):
        """(Deprecated - use RSA authentication instead /login/v1/pubkey/app/authenticate)  PROVISIONAL - Authenticate an application in a delegated context.   # noqa: E501

        Based on the SSL client certificate presented by the TLS layer, authenticate the API caller and return an application session.   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = auth_api.v1_app_authenticate_post(async_req=True)
        >>> result = thread.get()


        Keyword Args:
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _spec_property_naming (bool): True if the variable names in the input data
                are serialized names, as specified in the OpenAPI document.
                False if the variable names in the input data
                are pythonic names, e.g. snake case (default)
            _content_type (str/None): force body content-type.
                Default is None and content-type will be predicted by allowed
                content-types and body.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            Token
                If the method is called asynchronously, returns the request
                thread.
        """
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_spec_property_naming'] = kwargs.get(
            '_spec_property_naming', False
        )
        kwargs['_content_type'] = kwargs.get(
            '_content_type')
        kwargs['_host_index'] = kwargs.get('_host_index')
        return self.v1_app_authenticate_post_endpoint.call_with_http_info(**kwargs)

    def v1_app_user_uid_authenticate_post(
        self,
        uid,
        session_token,
        **kwargs
    ):
        """(Deprecated - use RSA authentication instead /login/v1/app/user/{uid}/authenticate)  PROVISIONAL - Authenticate an application in a delegated context to act on behalf of a user   # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = auth_api.v1_app_user_uid_authenticate_post(uid, session_token, async_req=True)
        >>> result = thread.get()

        Args:
            uid (int): user id
            session_token (str): Authorization token obtains from app/authenicate API

        Keyword Args:
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _spec_property_naming (bool): True if the variable names in the input data
                are serialized names, as specified in the OpenAPI document.
                False if the variable names in the input data
                are pythonic names, e.g. snake case (default)
            _content_type (str/None): force body content-type.
                Default is None and content-type will be predicted by allowed
                content-types and body.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            OboAuthResponse
                If the method is called asynchronously, returns the request
                thread.
        """
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_spec_property_naming'] = kwargs.get(
            '_spec_property_naming', False
        )
        kwargs['_content_type'] = kwargs.get(
            '_content_type')
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['uid'] = \
            uid
        kwargs['session_token'] = \
            session_token
        return self.v1_app_user_uid_authenticate_post_endpoint.call_with_http_info(**kwargs)

    def v1_app_username_username_authenticate_post(
        self,
        username,
        session_token,
        **kwargs
    ):
        """(Deprecated - use RSA authentication instead /login/v1/app/username/{username}/authenticate)  PROVISIONAL - Authenticate an application in a delegated context to act on behalf of a user   # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = auth_api.v1_app_username_username_authenticate_post(username, session_token, async_req=True)
        >>> result = thread.get()

        Args:
            username (str): username
            session_token (str): Authorization token obtains from app/authenicate API

        Keyword Args:
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _spec_property_naming (bool): True if the variable names in the input data
                are serialized names, as specified in the OpenAPI document.
                False if the variable names in the input data
                are pythonic names, e.g. snake case (default)
            _content_type (str/None): force body content-type.
                Default is None and content-type will be predicted by allowed
                content-types and body.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            OboAuthResponse
                If the method is called asynchronously, returns the request
                thread.
        """
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_spec_property_naming'] = kwargs.get(
            '_spec_property_naming', False
        )
        kwargs['_content_type'] = kwargs.get(
            '_content_type')
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['username'] = \
            username
        kwargs['session_token'] = \
            session_token
        return self.v1_app_username_username_authenticate_post_endpoint.call_with_http_info(**kwargs)

    def v1_authenticate_extension_app_post(
        self,
        auth_request,
        **kwargs
    ):
        """(Deprecated - use RSA authentication instead /login/v1/pubkey/app/authenticate/extensionApp)  Authenticate a client-extension application   # noqa: E501

        Based on the application's SSL client certificate presented by the TLS layer, it authenticates the client-extension application and return a symphony verification token.   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = auth_api.v1_authenticate_extension_app_post(auth_request, async_req=True)
        >>> result = thread.get()

        Args:
            auth_request (ExtensionAppAuthenticateRequest): application generated token

        Keyword Args:
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _spec_property_naming (bool): True if the variable names in the input data
                are serialized names, as specified in the OpenAPI document.
                False if the variable names in the input data
                are pythonic names, e.g. snake case (default)
            _content_type (str/None): force body content-type.
                Default is None and content-type will be predicted by allowed
                content-types and body.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            ExtensionAppTokens
                If the method is called asynchronously, returns the request
                thread.
        """
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_spec_property_naming'] = kwargs.get(
            '_spec_property_naming', False
        )
        kwargs['_content_type'] = kwargs.get(
            '_content_type')
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['auth_request'] = \
            auth_request
        return self.v1_authenticate_extension_app_post_endpoint.call_with_http_info(**kwargs)

    def v1_authenticate_post(
        self,
        **kwargs
    ):
        """Authenticate.  # noqa: E501

        Based on the SSL client certificate presented by the TLS layer, authenticate the API caller and return a session token.   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = auth_api.v1_authenticate_post(async_req=True)
        >>> result = thread.get()


        Keyword Args:
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _spec_property_naming (bool): True if the variable names in the input data
                are serialized names, as specified in the OpenAPI document.
                False if the variable names in the input data
                are pythonic names, e.g. snake case (default)
            _content_type (str/None): force body content-type.
                Default is None and content-type will be predicted by allowed
                content-types and body.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            Token
                If the method is called asynchronously, returns the request
                thread.
        """
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_spec_property_naming'] = kwargs.get(
            '_spec_property_naming', False
        )
        kwargs['_content_type'] = kwargs.get(
            '_content_type')
        kwargs['_host_index'] = kwargs.get('_host_index')
        return self.v1_authenticate_post_endpoint.call_with_http_info(**kwargs)

    def v1_logout_post(
        self,
        session_token,
        **kwargs
    ):
        """Logout.  # noqa: E501

        Logout a users session.   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = auth_api.v1_logout_post(session_token, async_req=True)
        >>> result = thread.get()

        Args:
            session_token (str): the session token to logout.

        Keyword Args:
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _spec_property_naming (bool): True if the variable names in the input data
                are serialized names, as specified in the OpenAPI document.
                False if the variable names in the input data
                are pythonic names, e.g. snake case (default)
            _content_type (str/None): force body content-type.
                Default is None and content-type will be predicted by allowed
                content-types and body.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            SuccessResponse
                If the method is called asynchronously, returns the request
                thread.
        """
        kwargs['async_req'] = kwargs.get(
            'async_req', False
        )
        kwargs['_return_http_data_only'] = kwargs.get(
            '_return_http_data_only', True
        )
        kwargs['_preload_content'] = kwargs.get(
            '_preload_content', True
        )
        kwargs['_request_timeout'] = kwargs.get(
            '_request_timeout', None
        )
        kwargs['_check_input_type'] = kwargs.get(
            '_check_input_type', True
        )
        kwargs['_check_return_type'] = kwargs.get(
            '_check_return_type', True
        )
        kwargs['_spec_property_naming'] = kwargs.get(
            '_spec_property_naming', False
        )
        kwargs['_content_type'] = kwargs.get(
            '_content_type')
        kwargs['_host_index'] = kwargs.get('_host_index')
        kwargs['session_token'] = \
            session_token
        return self.v1_logout_post_endpoint.call_with_http_info(**kwargs)

