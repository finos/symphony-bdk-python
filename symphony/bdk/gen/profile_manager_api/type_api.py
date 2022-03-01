"""
    Symphony Profile Manager

    Profile Manager is a microservice to manage users profile and groups  # noqa: E501

    The version of the OpenAPI document: 1.0.0
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
from symphony.bdk.gen.profile_manager_model.error import Error
from symphony.bdk.gen.profile_manager_model.sort_order import SortOrder
from symphony.bdk.gen.profile_manager_model.status import Status
from symphony.bdk.gen.profile_manager_model.type import Type
from symphony.bdk.gen.profile_manager_model.type_list import TypeList


class TypeApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        self.get_type_endpoint = _Endpoint(
            settings={
                'response_type': (Type,),
                'auth': [
                    'bearerAuth'
                ],
                'endpoint_path': '/v1/types/{typeId}',
                'operation_id': 'get_type',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'x_symphony_host',
                    'type_id',
                ],
                'required': [
                    'x_symphony_host',
                    'type_id',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                    'x_symphony_host',
                ]
            },
            root_map={
                'validations': {
                    ('x_symphony_host',): {

                        'min_length': 1,
                    },
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'x_symphony_host':
                        (str,),
                    'type_id':
                        (str,),
                },
                'attribute_map': {
                    'x_symphony_host': 'X-Symphony-Host',
                    'type_id': 'typeId',
                },
                'location_map': {
                    'x_symphony_host': 'header',
                    'type_id': 'path',
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
        self.list_types_endpoint = _Endpoint(
            settings={
                'response_type': (TypeList,),
                'auth': [
                    'bearerAuth'
                ],
                'endpoint_path': '/v1/types',
                'operation_id': 'list_types',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'x_symphony_host',
                    'status',
                    'before',
                    'after',
                    'limit',
                    'sort_order',
                ],
                'required': [
                    'x_symphony_host',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                    'x_symphony_host',
                ]
            },
            root_map={
                'validations': {
                    ('x_symphony_host',): {

                        'min_length': 1,
                    },
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'x_symphony_host':
                        (str,),
                    'status':
                        (Status,),
                    'before':
                        (str,),
                    'after':
                        (str,),
                    'limit':
                        (int,),
                    'sort_order':
                        (SortOrder,),
                },
                'attribute_map': {
                    'x_symphony_host': 'X-Symphony-Host',
                    'status': 'status',
                    'before': 'before',
                    'after': 'after',
                    'limit': 'limit',
                    'sort_order': 'sortOrder',
                },
                'location_map': {
                    'x_symphony_host': 'header',
                    'status': 'query',
                    'before': 'query',
                    'after': 'query',
                    'limit': 'query',
                    'sort_order': 'query',
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

    def get_type(
        self,
        x_symphony_host,
        type_id,
        **kwargs
    ):
        """Retrieve a type  # noqa: E501

        Retrieve a type  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = profile_manager_api.get_type(x_symphony_host, type_id, async_req=True)
        >>> result = thread.get()

        Args:
            x_symphony_host (str):
            type_id (str): Type id

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
            Type
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
        kwargs['x_symphony_host'] = \
            x_symphony_host
        kwargs['type_id'] = \
            type_id
        return self.get_type_endpoint.call_with_http_info(**kwargs)

    def list_types(
        self,
        x_symphony_host,
        **kwargs
    ):
        """List all types  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = profile_manager_api.list_types(x_symphony_host, async_req=True)
        >>> result = thread.get()

        Args:
            x_symphony_host (str):

        Keyword Args:
            status (Status): [optional]
            before (str): NOT SUPPORTED YET, currently ignored. Cursor that points to the start of the current page of data. If not present, the current page is the first page. [optional]
            after (str): cursor that points to the end of the current page of data. If not present, the current page is the last page. [optional]
            limit (int): numbers of items to return. [optional]
            sort_order (SortOrder): items sorting direction (ordered by createdDate). [optional]
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
            TypeList
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
        kwargs['x_symphony_host'] = \
            x_symphony_host
        return self.list_types_endpoint.call_with_http_info(**kwargs)

