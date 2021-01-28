from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.gen.agent_api.attachments_api import AttachmentsApi
from symphony.bdk.gen.agent_api.messages_api import MessagesApi
from symphony.bdk.gen.agent_model.v4_import_response import V4ImportResponse
from symphony.bdk.gen.agent_model.v4_imported_message import V4ImportedMessage
from symphony.bdk.gen.agent_model.v4_message import V4Message
from symphony.bdk.gen.agent_model.v4_message_blast_response import V4MessageBlastResponse
from symphony.bdk.gen.agent_model.v4_message_import_list import V4MessageImportList
from symphony.bdk.gen.api_client import Endpoint
from symphony.bdk.gen.model_utils import (
    file_type
)
from symphony.bdk.gen.pod_api.default_api import DefaultApi
from symphony.bdk.gen.pod_api.message_api import MessageApi
from symphony.bdk.gen.pod_api.message_suppression_api import MessageSuppressionApi
from symphony.bdk.gen.pod_api.pod_api import PodApi
from symphony.bdk.gen.pod_api.streams_api import StreamsApi
from symphony.bdk.gen.pod_model.message_metadata_response import MessageMetadataResponse
from symphony.bdk.gen.pod_model.message_receipt_detail_response import MessageReceiptDetailResponse
from symphony.bdk.gen.pod_model.message_status import MessageStatus
from symphony.bdk.gen.pod_model.message_suppression_response import MessageSuppressionResponse
from symphony.bdk.gen.pod_model.stream_attachment_item import StreamAttachmentItem


class MultiAttachmentsMessagesApi(MessagesApi):

    def __init__(self, api_client=None):
        super().__init__(api_client)

        def __v4_message_create_post(self, **kwargs):
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
            return self.call_with_http_info(**kwargs)

        self.v4_stream_sid_multi_attachment_message_create_post = Endpoint(
            settings={
                'response_type': (V4Message,),
                'auth': [],
                'endpoint_path': '/v4/stream/{sid}/message/create',
                'operation_id': 'v4_stream_sid_message_create_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'sid',
                    'session_token',
                    'key_manager_token',
                    'message',
                    'data',
                    'version',
                    'attachment',
                    'preview',
                ],
                'required': [
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
                    'sid':
                        (str,),
                    'session_token':
                        (str,),
                    'key_manager_token':
                        (str,),
                    'message':
                        (str,),
                    'data':
                        (str,),
                    'version':
                        (str,),
                    'attachment':
                        ([file_type],),
                    'preview':
                        ([file_type],),
                },
                'attribute_map': {
                    'sid': 'sid',
                    'session_token': 'sessionToken',
                    'key_manager_token': 'keyManagerToken',
                    'message': 'message',
                    'data': 'data',
                    'version': 'version',
                    'attachment': 'attachment',
                    'preview': 'preview',
                },
                'location_map': {
                    'sid': 'path',
                    'session_token': 'header',
                    'key_manager_token': 'header',
                    'message': 'form',
                    'data': 'form',
                    'version': 'form',
                    'attachment': 'form',
                    'preview': 'form',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [
                    'multipart/form-data'
                ]
            },
            api_client=api_client,
            callable=__v4_message_create_post
        )

        self.v4_multi_attachment_message_blast_post = Endpoint(
            settings={
                'response_type': (V4MessageBlastResponse,),
                'auth': [],
                'endpoint_path': '/v4/message/blast',
                'operation_id': 'v4_message_blast_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'session_token',
                    'sids',
                    'key_manager_token',
                    'message',
                    'data',
                    'version',
                    'attachment',
                    'preview',
                ],
                'required': [
                    'session_token',
                    'sids',
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
                    'sids':
                        ([str],),
                    'key_manager_token':
                        (str,),
                    'message':
                        (str,),
                    'data':
                        (str,),
                    'version':
                        (str,),
                    'attachment':
                        ([file_type],),
                    'preview':
                        ([file_type],),
                },
                'attribute_map': {
                    'session_token': 'sessionToken',
                    'sids': 'sids',
                    'key_manager_token': 'keyManagerToken',
                    'message': 'message',
                    'data': 'data',
                    'version': 'version',
                    'attachment': 'attachment',
                    'preview': 'preview',
                },
                'location_map': {
                    'session_token': 'header',
                    'sids': 'form',
                    'key_manager_token': 'header',
                    'message': 'form',
                    'data': 'form',
                    'version': 'form',
                    'attachment': 'form',
                    'preview': 'form',
                },
                'collection_format_map': {
                    'sids': 'csv',
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [
                    'multipart/form-data'
                ]
            },
            api_client=api_client,
            callable=__v4_message_create_post
        )


class MessageService:
    def __init__(self, messages_api: MultiAttachmentsMessagesApi,
                 message_api: MessageApi,
                 message_suppression_api: MessageSuppressionApi,
                 streams_api: StreamsApi,
                 pod_api: PodApi,
                 attachment_api: AttachmentsApi,
                 default_api: DefaultApi,
                 auth_session: AuthSession
                 ):
        self._messages_api = messages_api
        self._message_api = message_api
        self._message_suppression_api = message_suppression_api
        self._streams_api = streams_api
        self._pod_api = pod_api
        self._attachment_api = attachment_api
        self._default_api = default_api
        self._auth_session = auth_session

    async def list_messages(self, stream_id: str, since: int = 0, **kwargs) -> [V4Message]:
        params = {
            'sid': stream_id,
            'since': since,
            'session_token': self._auth_session.session_token,
            'key_manager_token': self._auth_session.key_manager_token
        }
        params.update(kwargs)
        message_list = await self._messages_api.v4_stream_sid_message_get(**params)
        return message_list.value

    async def send_message(self, stream_id: str, message: str, **kwargs) -> V4Message:
        if kwargs.get("attachment") is not None:
            attachment = kwargs["attachment"]
            kwargs["attachment"] = attachment if type(attachment) is list else [attachment]
        if kwargs.get("preview") is not None:
            preview = kwargs["preview"]
            kwargs["preview"] = preview if type(preview) is list else [preview]

        params = {
            'sid': stream_id,
            'session_token': self._auth_session.session_token,
            'key_manager_token': self._auth_session.key_manager_token,
            'message': message
        }
        params.update(kwargs)
        return await self._messages_api.v4_stream_sid_multi_attachment_message_create_post(**params)

    async def blast_message(self, stream_ids: [str], message: str, **kwargs):
        if kwargs.get("attachment") is not None:
            attachment = kwargs["attachment"]
            kwargs["attachment"] = attachment if type(attachment) is list else [attachment]
        if kwargs.get("preview") is not None:
            preview = kwargs["preview"]
            kwargs["preview"] = preview if type(preview) is list else [preview]

        params = {
            'sids': stream_ids,
            'session_token': self._auth_session.session_token,
            'key_manager_token': self._auth_session.key_manager_token,
            'message': message
        }
        params.update(kwargs)
        return await self._messages_api.v4_multi_attachment_message_blast_post(**params)

    async def import_messages(self, messages: [V4ImportedMessage]) -> [V4ImportResponse]:
        params = {
            'message_list': V4MessageImportList(value=messages),
            'session_token': self._auth_session.session_token,
            'key_manager_token': self._auth_session.key_manager_token
        }
        import_response_list = await self._messages_api.v4_message_import_post(**params)
        return import_response_list.value

    async def get_attachment(self, stream_id: str, message_id: str, attachment_id: str):
        params = {
            'sid': stream_id,
            'file_id': attachment_id,
            'message_id': message_id,
            'session_token': self._auth_session.session_token,
            'key_manager_token': self._auth_session.key_manager_token
        }
        return await self._attachment_api.v1_stream_sid_attachment_get(**params)

    async def suppress_message(self, message_id: str) -> MessageSuppressionResponse:
        params = {
            'id': message_id,
            'session_token': self._auth_session.session_token
        }
        return await self._message_suppression_api.v1_admin_messagesuppression_id_suppress_post(**params)

    async def get_message_status(self, message_id: str) -> MessageStatus:
        params = {
            'mid': message_id,
            'session_token': self._auth_session.session_token
        }
        return await self._message_api.v1_message_mid_status_get(**params)

    async def get_attachment_types(self) -> [str]:
        params = {
            'session_token': self._auth_session.session_token
        }
        type_list = await self._pod_api.v1_files_allowed_types_get(**params)
        return type_list.value

    async def get_message(self, message_id: str) -> V4Message:
        params = {
            'id': message_id,
            'session_token': self._auth_session.session_token,
            'key_manager_token': self._auth_session.key_manager_token
        }
        return await self._messages_api.v1_message_id_get(**params)

    async def list_attachments(self, stream_id: str, **kwargs) -> [StreamAttachmentItem]:
        params = {
            'sid': stream_id,
            'session_token': self._auth_session.session_token
        }
        params.update(kwargs)
        attachment_list = await self._streams_api.v1_streams_sid_attachments_get(**params)
        return attachment_list.value

    async def list_message_receipts(self, message_id: str, **kwargs) -> MessageReceiptDetailResponse:
        params = {
            'message_id': message_id,
            'session_token': self._auth_session.session_token
        }
        params.update(kwargs)
        return await self._default_api.v1_admin_messages_message_id_receipts_get(**params)

    async def get_message_relationships(self, message_id: str) -> MessageMetadataResponse:
        params = {
            'message_id': message_id,
            'session_token': self._auth_session.session_token
        }
        return await self._default_api.v1_admin_messages_message_id_metadata_relationships_get(**params)
