"""
    Pod API

    This document refers to Symphony API calls that do not need encryption or decryption of content.  - sessionToken can be obtained by calling the authenticationAPI on the symphony back end and the key manager respectively. Refer to the methods described in authenticatorAPI.yaml. - Actions are defined to be atomic, ie will succeed in their entirety or fail and have changed nothing. - If it returns a 40X status then it will have made no change to the system even if ome subset of the request would have succeeded. - If this contract cannot be met for any reason then this is an error and the response code will be 50X.   # noqa: E501

    The version of the OpenAPI document: 20.10.0
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
from symphony.bdk.gen.pod_model.user_connection import UserConnection
from symphony.bdk.gen.pod_model.user_connection_list import UserConnectionList
from symphony.bdk.gen.pod_model.user_connection_request import UserConnectionRequest


class ConnectionApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        def __v1_connection_accept_post(
            self,
            session_token,
            connection_request,
            **kwargs
        ):
            """Accept the connection request for the requesting user  # noqa: E501

            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = pod_api.v1_connection_accept_post(session_token, connection_request, async_req=True)
            >>> result = thread.get()

            Args:
                session_token (str): Session authentication token.
                connection_request (UserConnectionRequest):

            Keyword Args:
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (float/tuple): timeout setting for this request. If one
                    number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                UserConnection
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
            kwargs['_host_index'] = kwargs.get('_host_index')
            kwargs['session_token'] = \
                session_token
            kwargs['connection_request'] = \
                connection_request
            return self.call_with_http_info(**kwargs)

        self.v1_connection_accept_post = _Endpoint(
            settings={
                'response_type': (UserConnection,),
                'auth': [],
                'endpoint_path': '/v1/connection/accept',
                'operation_id': 'v1_connection_accept_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'session_token',
                    'connection_request',
                ],
                'required': [
                    'session_token',
                    'connection_request',
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
                    'connection_request':
                        (UserConnectionRequest,),
                },
                'attribute_map': {
                    'session_token': 'sessionToken',
                },
                'location_map': {
                    'session_token': 'header',
                    'connection_request': 'body',
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
            api_client=api_client,
            callable=__v1_connection_accept_post
        )

        def __v1_connection_create_post(
            self,
            session_token,
            connection_request,
            **kwargs
        ):
            """Sends an invitation to connect with another user  # noqa: E501

            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = pod_api.v1_connection_create_post(session_token, connection_request, async_req=True)
            >>> result = thread.get()

            Args:
                session_token (str): Session authentication token.
                connection_request (UserConnectionRequest):

            Keyword Args:
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (float/tuple): timeout setting for this request. If one
                    number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                UserConnection
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
            kwargs['_host_index'] = kwargs.get('_host_index')
            kwargs['session_token'] = \
                session_token
            kwargs['connection_request'] = \
                connection_request
            return self.call_with_http_info(**kwargs)

        self.v1_connection_create_post = _Endpoint(
            settings={
                'response_type': (UserConnection,),
                'auth': [],
                'endpoint_path': '/v1/connection/create',
                'operation_id': 'v1_connection_create_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'session_token',
                    'connection_request',
                ],
                'required': [
                    'session_token',
                    'connection_request',
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
                    'connection_request':
                        (UserConnectionRequest,),
                },
                'attribute_map': {
                    'session_token': 'sessionToken',
                },
                'location_map': {
                    'session_token': 'header',
                    'connection_request': 'body',
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
            api_client=api_client,
            callable=__v1_connection_create_post
        )

        def __v1_connection_list_get(
            self,
            session_token,
            **kwargs
        ):
            """List of requesting user's connection  # noqa: E501

            This retrieves all connections of the requesting user. (i.e. both connections in which the requesting user is the sender and those in which the requesting user is the inivtee) By default, if you haven't specified the connection status to filter on, this call will only return results for both \"pending_incoming\" and \"pending_outgoing\". You can optionally filter by userIds to further restrict the results of a specific connection status. If the users are in the same private pod, the users have an implicit connection status of \"accepted\". Those users will not be returned in the response if you don't specify the connection status as \"accepted\" (default is \"pending\") and the explicit userIds in the request.   # noqa: E501
            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = pod_api.v1_connection_list_get(session_token, async_req=True)
            >>> result = thread.get()

            Args:
                session_token (str): Session authentication token.

            Keyword Args:
                status (str): Filter the connection list based on the connection status. The connection status can only be pending_incoming, pending_outgoing, accepted, rejected, or all (all of the above) . [optional]
                user_ids (str): The userIds parameter should be specified as a comma delimited list of user ids and can be used to restrict the results of a specific connection. Note that this is particularly important if the caller intends to retrieve results for implicit connection (user within the same pod). Implicit connections will not be included in the response if userId is not provided. . [optional]
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (float/tuple): timeout setting for this request. If one
                    number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                UserConnectionList
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
            kwargs['_host_index'] = kwargs.get('_host_index')
            kwargs['session_token'] = \
                session_token
            return self.call_with_http_info(**kwargs)

        self.v1_connection_list_get = _Endpoint(
            settings={
                'response_type': (UserConnectionList,),
                'auth': [],
                'endpoint_path': '/v1/connection/list',
                'operation_id': 'v1_connection_list_get',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'session_token',
                    'status',
                    'user_ids',
                ],
                'required': [
                    'session_token',
                ],
                'nullable': [
                ],
                'enum': [
                    'status',
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                    ('status',): {

                        "PENDING_INCOMING": "PENDING_INCOMING",
                        "PENDING_OUTGOING": "PENDING_OUTGOING",
                        "ACCEPTED": "ACCEPTED",
                        "REJECTED": "REJECTED",
                        "ALL": "ALL"
                    },
                },
                'openapi_types': {
                    'session_token':
                        (str,),
                    'status':
                        (str,),
                    'user_ids':
                        (str,),
                },
                'attribute_map': {
                    'session_token': 'sessionToken',
                    'status': 'status',
                    'user_ids': 'userIds',
                },
                'location_map': {
                    'session_token': 'header',
                    'status': 'query',
                    'user_ids': 'query',
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
            api_client=api_client,
            callable=__v1_connection_list_get
        )

        def __v1_connection_reject_post(
            self,
            session_token,
            connection_request,
            **kwargs
        ):
            """Reject the connection request for the requesting user.  # noqa: E501

            Reject the connection between the requesting user and request sender. If both users are in the same private pod, an error will be returned because both users have an implicit connection which cannot be rejected.   # noqa: E501
            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = pod_api.v1_connection_reject_post(session_token, connection_request, async_req=True)
            >>> result = thread.get()

            Args:
                session_token (str): Session authentication token.
                connection_request (UserConnectionRequest):

            Keyword Args:
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (float/tuple): timeout setting for this request. If one
                    number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                UserConnection
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
            kwargs['_host_index'] = kwargs.get('_host_index')
            kwargs['session_token'] = \
                session_token
            kwargs['connection_request'] = \
                connection_request
            return self.call_with_http_info(**kwargs)

        self.v1_connection_reject_post = _Endpoint(
            settings={
                'response_type': (UserConnection,),
                'auth': [],
                'endpoint_path': '/v1/connection/reject',
                'operation_id': 'v1_connection_reject_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'session_token',
                    'connection_request',
                ],
                'required': [
                    'session_token',
                    'connection_request',
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
                    'connection_request':
                        (UserConnectionRequest,),
                },
                'attribute_map': {
                    'session_token': 'sessionToken',
                },
                'location_map': {
                    'session_token': 'header',
                    'connection_request': 'body',
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
            api_client=api_client,
            callable=__v1_connection_reject_post
        )

        def __v1_connection_user_uid_remove_post(
            self,
            session_token,
            uid,
            **kwargs
        ):
            """Removes a connection with a user.  # noqa: E501

            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = pod_api.v1_connection_user_uid_remove_post(session_token, uid, async_req=True)
            >>> result = thread.get()

            Args:
                session_token (str): Session authentication token.
                uid (int): User ID as a decimal integer 

            Keyword Args:
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (float/tuple): timeout setting for this request. If one
                    number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
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
            kwargs['_host_index'] = kwargs.get('_host_index')
            kwargs['session_token'] = \
                session_token
            kwargs['uid'] = \
                uid
            return self.call_with_http_info(**kwargs)

        self.v1_connection_user_uid_remove_post = _Endpoint(
            settings={
                'response_type': (SuccessResponse,),
                'auth': [],
                'endpoint_path': '/v1/connection/user/{uid}/remove',
                'operation_id': 'v1_connection_user_uid_remove_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'session_token',
                    'uid',
                ],
                'required': [
                    'session_token',
                    'uid',
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
                },
                'attribute_map': {
                    'session_token': 'sessionToken',
                    'uid': 'uid',
                },
                'location_map': {
                    'session_token': 'header',
                    'uid': 'path',
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
            api_client=api_client,
            callable=__v1_connection_user_uid_remove_post
        )

        def __v1_connection_user_user_id_info_get(
            self,
            session_token,
            user_id,
            **kwargs
        ):
            """The status of the connection invitation to another user.  # noqa: E501

            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = pod_api.v1_connection_user_user_id_info_get(session_token, user_id, async_req=True)
            >>> result = thread.get()

            Args:
                session_token (str): Session authentication token.
                user_id (str): user Id

            Keyword Args:
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (float/tuple): timeout setting for this request. If one
                    number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                UserConnection
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
            kwargs['_host_index'] = kwargs.get('_host_index')
            kwargs['session_token'] = \
                session_token
            kwargs['user_id'] = \
                user_id
            return self.call_with_http_info(**kwargs)

        self.v1_connection_user_user_id_info_get = _Endpoint(
            settings={
                'response_type': (UserConnection,),
                'auth': [],
                'endpoint_path': '/v1/connection/user/{userId}/info',
                'operation_id': 'v1_connection_user_user_id_info_get',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'session_token',
                    'user_id',
                ],
                'required': [
                    'session_token',
                    'user_id',
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
                    'user_id':
                        (str,),
                },
                'attribute_map': {
                    'session_token': 'sessionToken',
                    'user_id': 'userId',
                },
                'location_map': {
                    'session_token': 'header',
                    'user_id': 'path',
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
            api_client=api_client,
            callable=__v1_connection_user_user_id_info_get
        )
