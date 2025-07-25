"""
    Pod API

    This document refers to Symphony API calls that do not need encryption or decryption of content.  - sessionToken can be obtained by calling the authenticationAPI on the symphony back end and the key manager respectively. Refer to the methods described in authenticatorAPI.yaml. - Actions are defined to be atomic, ie will succeed in their entirety or fail and have changed nothing. - If it returns a 40X status then it will have made no change to the system even if ome subset of the request would have succeeded. - If this contract cannot be met for any reason then this is an error and the response code will be 50X.   # noqa: E501

    The version of the OpenAPI document: 20.17.1
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
from symphony.bdk.gen.pod_model.error import Error
from symphony.bdk.gen.pod_model.success_response import SuccessResponse
from symphony.bdk.gen.pod_model.user_search_query import UserSearchQuery
from symphony.bdk.gen.pod_model.user_search_results import UserSearchResults
from symphony.bdk.gen.pod_model.user_v2 import UserV2
from symphony.bdk.gen.pod_model.v1_user_sessions import V1UserSessions
from symphony.bdk.gen.pod_model.v2_user_list import V2UserList


class UsersApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        self.v1_user_search_post_endpoint = _Endpoint(
            settings={
                'response_type': (UserSearchResults,),
                'auth': [],
                'endpoint_path': '/v1/user/search',
                'operation_id': 'v1_user_search_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'session_token',
                    'search_request',
                    'skip',
                    'limit',
                    'local',
                ],
                'required': [
                    'session_token',
                    'search_request',
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
                    'search_request':
                        (UserSearchQuery,),
                    'skip':
                        (int,),
                    'limit':
                        (int,),
                    'local':
                        (bool,),
                },
                'attribute_map': {
                    'session_token': 'sessionToken',
                    'skip': 'skip',
                    'limit': 'limit',
                    'local': 'local',
                },
                'location_map': {
                    'session_token': 'header',
                    'search_request': 'body',
                    'skip': 'query',
                    'limit': 'query',
                    'local': 'query',
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
        self.v1_users_uid_sessions_get_endpoint = _Endpoint(
            settings={
                'response_type': (V1UserSessions,),
                'auth': [],
                'endpoint_path': '/v1/users/{uid}/sessions',
                'operation_id': 'v1_users_uid_sessions_get',
                'http_method': 'GET',
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
                        (str,),
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
        self.v1_users_uid_sessions_logout_post_endpoint = _Endpoint(
            settings={
                'response_type': (SuccessResponse,),
                'auth': [],
                'endpoint_path': '/v1/users/{uid}/sessions/logout',
                'operation_id': 'v1_users_uid_sessions_logout_post',
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
                        (str,),
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
        self.v1_users_uid_sessions_sid_logout_post_endpoint = _Endpoint(
            settings={
                'response_type': (SuccessResponse,),
                'auth': [],
                'endpoint_path': '/v1/users/{uid}/sessions/{sid}/logout',
                'operation_id': 'v1_users_uid_sessions_sid_logout_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'uid',
                    'sid',
                    'session_token',
                ],
                'required': [
                    'uid',
                    'sid',
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
                        (str,),
                    'sid':
                        (str,),
                    'session_token':
                        (str,),
                },
                'attribute_map': {
                    'uid': 'uid',
                    'sid': 'sid',
                    'session_token': 'sessionToken',
                },
                'location_map': {
                    'uid': 'path',
                    'sid': 'path',
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
        self.v2_user_get_endpoint = _Endpoint(
            settings={
                'response_type': (UserV2,),
                'auth': [],
                'endpoint_path': '/v2/user',
                'operation_id': 'v2_user_get',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'session_token',
                    'uid',
                    'email',
                    'username',
                    'local',
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
                    'uid':
                        (int,),
                    'email':
                        (str,),
                    'username':
                        (str,),
                    'local':
                        (bool,),
                },
                'attribute_map': {
                    'session_token': 'sessionToken',
                    'uid': 'uid',
                    'email': 'email',
                    'username': 'username',
                    'local': 'local',
                },
                'location_map': {
                    'session_token': 'header',
                    'uid': 'query',
                    'email': 'query',
                    'username': 'query',
                    'local': 'query',
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
        self.v3_users_get_endpoint = _Endpoint(
            settings={
                'response_type': (V2UserList,),
                'auth': [],
                'endpoint_path': '/v3/users',
                'operation_id': 'v3_users_get',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'session_token',
                    'uid',
                    'email',
                    'username',
                    'local',
                    'active',
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
                    'uid':
                        (str,),
                    'email':
                        (str,),
                    'username':
                        (str,),
                    'local':
                        (bool,),
                    'active':
                        (bool,),
                },
                'attribute_map': {
                    'session_token': 'sessionToken',
                    'uid': 'uid',
                    'email': 'email',
                    'username': 'username',
                    'local': 'local',
                    'active': 'active',
                },
                'location_map': {
                    'session_token': 'header',
                    'uid': 'query',
                    'email': 'query',
                    'username': 'query',
                    'local': 'query',
                    'active': 'query',
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

    def v1_user_search_post(
        self,
        session_token,
        search_request,
        **kwargs
    ):
        """Search for users by name or email address  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = pod_api.v1_user_search_post(session_token, search_request, async_req=True)
        >>> result = thread.get()

        Args:
            session_token (str): Session authentication token.
            search_request (UserSearchQuery): search criteria

        Keyword Args:
            skip (int): number of records to skip. [optional]
            limit (int): Max number of records to return. If no value is provided, 50 is the default.. [optional]
            local (bool): If true then a local DB search will be performed and only local pod users will be returned. If absent or false then a directory search will be performed and users from other pods who are visible to the calling user will also be returned. . [optional]
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
            UserSearchResults
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
        kwargs['search_request'] = \
            search_request
        return self.v1_user_search_post_endpoint.call_with_http_info(**kwargs)

    def v1_users_uid_sessions_get(
        self,
        uid,
        session_token,
        **kwargs
    ):
        """Lists all sessions for the user identified by {uid}.   # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = pod_api.v1_users_uid_sessions_get(uid, session_token, async_req=True)
        >>> result = thread.get()

        Args:
            uid (str): The identifier of the user whose sessions are to be listed.
            session_token (str): Session authentication token.

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
            V1UserSessions
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
        return self.v1_users_uid_sessions_get_endpoint.call_with_http_info(**kwargs)

    def v1_users_uid_sessions_logout_post(
        self,
        uid,
        session_token,
        **kwargs
    ):
        """Ends all sessions for the user identified by {uid}.   # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = pod_api.v1_users_uid_sessions_logout_post(uid, session_token, async_req=True)
        >>> result = thread.get()

        Args:
            uid (str): The identifier of the user whose sessions are to be terminated.
            session_token (str): Session authentication token.

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
        kwargs['uid'] = \
            uid
        kwargs['session_token'] = \
            session_token
        return self.v1_users_uid_sessions_logout_post_endpoint.call_with_http_info(**kwargs)

    def v1_users_uid_sessions_sid_logout_post(
        self,
        uid,
        sid,
        session_token,
        **kwargs
    ):
        """Ends the session identified by {sid} for the user with the identifier {uid}.   # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = pod_api.v1_users_uid_sessions_sid_logout_post(uid, sid, session_token, async_req=True)
        >>> result = thread.get()

        Args:
            uid (str): The identifier of the user who owns the session to be terminated.
            sid (str): The identifier of the session to be terminated.
            session_token (str): Session authentication token.

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
        kwargs['uid'] = \
            uid
        kwargs['sid'] = \
            sid
        kwargs['session_token'] = \
            session_token
        return self.v1_users_uid_sessions_sid_logout_post_endpoint.call_with_http_info(**kwargs)

    def v2_user_get(
        self,
        session_token,
        **kwargs
    ):
        """Get user information  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = pod_api.v2_user_get(session_token, async_req=True)
        >>> result = thread.get()

        Args:
            session_token (str): Session authentication token.

        Keyword Args:
            uid (int): User ID as a decimal integer. [optional]
            email (str): Email address. [optional]
            username (str): login user name. [optional]
            local (bool): If true then a local DB search will be performed and only local pod users will be returned. If absent or false then a directory search will be performed and users from other pods who are visible to the calling user will also be returned. Note: for username search, the local flag must be true . [optional]
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
            UserV2
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
        return self.v2_user_get_endpoint.call_with_http_info(**kwargs)

    def v3_users_get(
        self,
        session_token,
        **kwargs
    ):
        """Search users by emails or ids. Only one of the search lists should be informed at a time. Search lists may containt up to 100 elements.   # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = pod_api.v3_users_get(session_token, async_req=True)
        >>> result = thread.get()

        Args:
            session_token (str): Session authentication token.

        Keyword Args:
            uid (str): User IDs as a list of decimal integers separated by comma. [optional]
            email (str): List of email addresses separated by comma. [optional]
            username (str): List of username separated by comma. [optional]
            local (bool): If true then a local DB search will be performed and only local pod users will be returned. If absent or false then a directory search will be performed and users from other pods who are visible to the calling user will also be returned. . [optional]
            active (bool): If not set all user status will be returned, if true all active users will be returned, if false all inactive users will be returned . [optional]
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
            V2UserList
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
        return self.v3_users_get_endpoint.call_with_http_info(**kwargs)

