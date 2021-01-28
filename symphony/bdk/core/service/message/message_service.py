from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.message.multi_attachments_messages_api import MultiAttachmentsMessagesApi
from symphony.bdk.gen.agent_api.attachments_api import AttachmentsApi
from symphony.bdk.gen.agent_model.v4_import_response import V4ImportResponse
from symphony.bdk.gen.agent_model.v4_imported_message import V4ImportedMessage
from symphony.bdk.gen.agent_model.v4_message import V4Message
from symphony.bdk.gen.agent_model.v4_message_blast_response import V4MessageBlastResponse
from symphony.bdk.gen.agent_model.v4_message_import_list import V4MessageImportList
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

    async def list_messages(
            self,
            stream_id: str,
            since: int = 0,
            skip: int = 0,
            limit: int = 50
    ) -> [V4Message]:
        params = {
            'sid': stream_id,
            'since': since,
            'session_token': self._auth_session.session_token,
            'key_manager_token': self._auth_session.key_manager_token,
            'skip': skip,
            'limit': limit
        }
        message_list = await self._messages_api.v4_stream_sid_message_get(**params)
        return message_list.value

    async def send_message(
            self,
            stream_id: str,
            message: str,
            data: str = '',
            version: str = '',
            attachment: [file_type] = None,
            preview: [file_type] = None
    ) -> V4Message:
        params = {
            'sid': stream_id,
            'session_token': self._auth_session.session_token,
            'key_manager_token': self._auth_session.key_manager_token,
            'message': message,
            'data': data,
            'version': version
        }
        if attachment is not None:
            params['attachment'] = attachment if type(attachment) is list else [attachment]
        if preview is not None:
            params['preview'] = preview if type(preview) is list else [preview]

        return await self._messages_api.v4_stream_sid_multi_attachment_message_create_post(**params)

    async def blast_message(
            self,
            stream_ids: [str],
            message: str,
            data: str = '',
            version: str = '',
            attachment: [file_type] = None,
            preview: [file_type] = None
    ) -> V4MessageBlastResponse:
        params = {
            'sids': stream_ids,
            'session_token': self._auth_session.session_token,
            'key_manager_token': self._auth_session.key_manager_token,
            'message': message,
            'data': data,
            'version': version
        }
        if attachment is not None:
            params['attachment'] = attachment if type(attachment) is list else [attachment]
        if preview is not None:
            params['preview'] = preview if type(preview) is list else [preview]

        return await self._messages_api.v4_multi_attachment_message_blast_post(**params)

    async def import_messages(
            self,
            messages: [V4ImportedMessage]
    ) -> [V4ImportResponse]:
        params = {
            'message_list': V4MessageImportList(value=messages),
            'session_token': self._auth_session.session_token,
            'key_manager_token': self._auth_session.key_manager_token
        }
        import_response_list = await self._messages_api.v4_message_import_post(**params)
        return import_response_list.value

    async def get_attachment(
            self,
            stream_id: str,
            message_id: str,
            attachment_id: str
    ):
        params = {
            'sid': stream_id,
            'file_id': attachment_id,
            'message_id': message_id,
            'session_token': self._auth_session.session_token,
            'key_manager_token': self._auth_session.key_manager_token
        }
        return await self._attachment_api.v1_stream_sid_attachment_get(**params)

    async def suppress_message(
            self,
            message_id: str
    ) -> MessageSuppressionResponse:
        params = {
            'id': message_id,
            'session_token': self._auth_session.session_token
        }
        return await self._message_suppression_api.v1_admin_messagesuppression_id_suppress_post(**params)

    async def get_message_status(
            self,
            message_id: str
    ) -> MessageStatus:
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

    async def get_message(
            self,
            message_id: str
    ) -> V4Message:
        params = {
            'id': message_id,
            'session_token': self._auth_session.session_token,
            'key_manager_token': self._auth_session.key_manager_token
        }
        return await self._messages_api.v1_message_id_get(**params)

    async def list_attachments(
            self,
            stream_id: str,
            since: int = None,
            to: int = None,
            limit: int = 50,
            sort_dir: str = 'ASC'
    ) -> [StreamAttachmentItem]:
        params = {
            'sid': stream_id,
            'session_token': self._auth_session.session_token,
            'limit': limit,
            'sort_dir': sort_dir
        }
        if since is not None:
            params['since'] = since
        if to is not None:
            params['to'] = to
        attachment_list = await self._streams_api.v1_streams_sid_attachments_get(**params)
        return attachment_list.value

    async def list_message_receipts(
            self,
            message_id: str
    ) -> MessageReceiptDetailResponse:
        params = {
            'message_id': message_id,
            'session_token': self._auth_session.session_token
        }
        return await self._default_api.v1_admin_messages_message_id_receipts_get(**params)

    async def get_message_relationships(
            self,
            message_id: str
    ) -> MessageMetadataResponse:
        params = {
            'message_id': message_id,
            'session_token': self._auth_session.session_token
        }
        return await self._default_api.v1_admin_messages_message_id_metadata_relationships_get(**params)
