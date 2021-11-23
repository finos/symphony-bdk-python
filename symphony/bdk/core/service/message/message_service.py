from typing import Union, List, Tuple, IO, AsyncGenerator

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig
from symphony.bdk.core.service.message.model import Message
from symphony.bdk.core.service.message.multi_attachments_messages_api import MultiAttachmentsMessagesApi
from symphony.bdk.core.service.pagination import offset_based_pagination
from symphony.bdk.gen.agent_api.attachments_api import AttachmentsApi
from symphony.bdk.gen.agent_model.message_search_query import MessageSearchQuery
from symphony.bdk.gen.agent_model.v4_import_response import V4ImportResponse
from symphony.bdk.gen.agent_model.v4_imported_message import V4ImportedMessage
from symphony.bdk.gen.agent_model.v4_message import V4Message
from symphony.bdk.gen.agent_model.v4_message_blast_response import V4MessageBlastResponse
from symphony.bdk.gen.agent_model.v4_message_import_list import V4MessageImportList
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

from symphony.bdk.core.retry import retry


class OboMessageService:
    """Class exposing OBO enabled endpoints for message management, e.g. send a message."""

    def __init__(self, messages_api: MultiAttachmentsMessagesApi, message_suppression_api: MessageSuppressionApi,
                 auth_session: AuthSession,
                 retry_config: BdkRetryConfig):
        self._messages_api = messages_api
        self._message_suppression_api = message_suppression_api
        self._auth_session = auth_session
        self._retry_config = retry_config

    async def send_message(
            self,
            stream_id: str,
            message: Union[str, Message],
            data=None,
            version: str = "",
            attachment: List[Union[IO, Tuple[IO, IO]]] = None
    ) -> V4Message:
        """Send a message to an existing stream.
        See: `Create Message <https://developers.symphony.com/restapi/reference#create-message-v4>`_

        :param stream_id: The ID of the stream to send the message to.
        :param message: a :py:class:`Message` instance or a string containing the MessageML content to be sent.
          If it is a :py:class:`Message` instance, other parameters will be ignored.
          If it is a string, ``<messageML>`` tags can be omitted.
        :param data: an object (e.g. dict) that will be serialized into JSON using ``json.dumps``.
        :param version: Optional message version in the format "major.minor".
          If empty, defaults to the latest supported version.
        :param attachment: One or more files (opened in binary or text mode) to be sent along with the message.
          Elements of the list can be attachment files or tuples of ``(attachment, preview)``.
          If one attachment has a preview, then all attachments must have a preview.
          The limit is set to 30Mb total size; also, it is recommended not to exceed 25 files.

        :return: a V4Message object containing the details of the sent message.
        """
        message_object = message if isinstance(message, Message) else Message(content=message, data=data,
                                                                              version=version, attachments=attachment)
        return await self._send_message(stream_id, message_object.content, message_object.data, message_object.version,
                                        message_object.attachments, message_object.previews)

    @retry
    async def _send_message(
            self,
            stream_id: str,
            message: str,
            data: str = "",
            version: str = "",
            attachment: List[IO] = None,
            preview: List[IO] = None
    ) -> V4Message:
        """Send a message to an existing stream.
        See: `Create Message <https://developers.symphony.com/restapi/reference#create-message-v4>`_

        :param stream_id: The ID of the stream to send the message to.
        :param message: The MessageML content to be sent.
        :param data: JSON data representing the objects contained in the message.
        :param version: Optional message version in the format "major.minor".
                        If empty, defaults to the latest supported version.
        :param attachment: One or more files to be sent along with the message.
                        The limit is set to 30Mb total size; also, it is recommended not to exceed 25 files.
        :param preview: Previews of the attachments which are sent along with the message.

        :return: a V4Message object containing the details of the sent message.

        """
        params = {
            "sid": stream_id,
            "session_token": await self._auth_session.session_token,
            "key_manager_token": await self._auth_session.key_manager_token,
            "message": message,
            "data": data,
            "version": version
        }
        if attachment is not None:
            params["attachment"] = attachment if isinstance(attachment, list) else [attachment]
        if preview is not None:
            params["preview"] = preview if isinstance(preview, list) else [preview]

        return await self._messages_api.v4_stream_sid_multi_attachment_message_create_post(**params)

    @retry
    async def suppress_message(
            self,
            message_id: str
    ) -> MessageSuppressionResponse:
        """Suppresses a message, preventing its contents from being displayed to users.
        See: `Suppress Message <https://developers.symphony.com/restapi/reference#suppress-message>`_

        :param message_id: Message ID of the message to be suppressed.

        :return: a MessageSuppressionResponse instance containing information about the message suppression.

        """
        params = {
            "id": message_id,
            "session_token": await self._auth_session.session_token
        }
        return await self._message_suppression_api.v1_admin_messagesuppression_id_suppress_post(**params)


class MessageService(OboMessageService):
    """Service class for managing messages.
    """

    def __init__(self, messages_api: MultiAttachmentsMessagesApi,
                 message_api: MessageApi,
                 message_suppression_api: MessageSuppressionApi,
                 streams_api: StreamsApi,
                 pod_api: PodApi,
                 attachment_api: AttachmentsApi,
                 default_api: DefaultApi,
                 auth_session: AuthSession,
                 retry_config: BdkRetryConfig):
        super().__init__(messages_api, message_suppression_api, auth_session, retry_config)
        self._message_api = message_api
        self._message_suppression_api = message_suppression_api
        self._streams_api = streams_api
        self._pod_api = pod_api
        self._attachment_api = attachment_api
        self._default_api = default_api

    @retry
    async def list_messages(
            self,
            stream_id: str,
            since: int = 0,
            skip: int = 0,
            limit: int = 50
    ) -> [V4Message]:
        """Get messages from an existing stream. Additionally returns any attachments associated with the message.
        See: `Messages <https://developers.symphony.com/restapi/reference#messages-v4>`_

        :param stream_id: The stream where to look for messages
        :param since: Timestamp of the earliest possible date of the first message returned.
        :param skip: Number of messages to skip. Default: 0
        :param limit: Maximum number of messages to return. Default: 50

        :return: the list of matching messages in the stream.

        """
        params = {
            "sid": stream_id,
            "since": since,
            "session_token": await self._auth_session.session_token,
            "key_manager_token": await self._auth_session.key_manager_token,
            "skip": skip,
            "limit": limit
        }
        message_list = await self._messages_api.v4_stream_sid_message_get(**params)
        return message_list.value

    async def blast_message(
            self,
            stream_ids: List[str],
            message: Union[str, Message],
            data=None,
            version: str = "",
            attachment: List[Union[IO, Tuple[IO, IO]]] = None
    ) -> V4MessageBlastResponse:
        """Send a message to multiple existing streams.
        See: `Blast Message <https://developers.symphony.com/restapi/reference#blast-message>`_

        :param stream_ids: The list of stream IDs to send the message to
        :param message: a :py:class:`Message` instance or a string containing the MessageML content to be sent.
          If it is a :py:class:`Message` instance, other parameters will be ignored.
          If it is a string, ``<messageML>`` tags can be omitted.
        :param data: an object (e.g. dict) that will be serialized into JSON using ``json.dumps``.
        :param version: Optional message version in the format "major.minor".
          If empty, defaults to the latest supported version.
        :param attachment: One or more files (opened in binary or text mode) to be sent along with the message.
          Elements of the list can be attachment files or tuples of ``(attachment, preview)``.
          If one attachment has a preview, then all attachments must have a preview.
          The limit is set to 30Mb total size; also, it is recommended not to exceed 25 files.
        :return:
        """
        message_object = message if isinstance(message, Message) else Message(content=message, data=data,
                                                                              version=version, attachments=attachment)
        return await self._blast_message(stream_ids, message_object.content, message_object.data,
                                         message_object.version, message_object.attachments, message_object.previews)

    @retry
    async def _blast_message(
            self,
            stream_ids: [str],
            message: str,
            data: str = "",
            version: str = "",
            attachment: List[IO] = None,
            preview: List[IO] = None
    ) -> V4MessageBlastResponse:
        """Send a message to multiple existing streams.
        See: `Blast Message <https://developers.symphony.com/restapi/reference#blast-message>`_

        :param stream_ids: The list of stream IDs to send the message to
        :param message: The messageML content to be sent.
        :param data: JSON data representing the objects contained in the message.
        :param version: Optional message version in the format "major.minor".
                        If empty, defaults to the latest supported version.
        :param attachment: One or more files to be sent along with the message.
                        The limit is set to 30Mb total size; also, it is recommended not to exceed 25 files.
        :param preview: Previews of the attachments which are sent along with the message.

        :return: a V4MessageBlastResponse object containing the details of the sent messages

        """
        params = {
            "sids": stream_ids,
            "session_token": await self._auth_session.session_token,
            "key_manager_token": await self._auth_session.key_manager_token,
            "message": message,
            "data": data,
            "version": version
        }
        if attachment is not None:
            params["attachment"] = attachment if isinstance(attachment, list) else [attachment]
        if preview is not None:
            params["preview"] = preview if isinstance(preview, list) else [preview]

        return await self._messages_api.v4_multi_attachment_message_blast_post(**params)

    @retry
    async def import_messages(
            self,
            messages: List[V4ImportedMessage]
    ) -> [V4ImportResponse]:
        """Imports a list of messages to Symphony.
        See: `Import Message <https://developers.symphony.com/restapi/reference#import-message-v4>`_

        :param messages: List of messages to import.

        :return: The list of imported messages

        """
        params = {
            "message_list": V4MessageImportList(value=messages),
            "session_token": await self._auth_session.session_token,
            "key_manager_token": await self._auth_session.key_manager_token
        }
        import_response_list = await self._messages_api.v4_message_import_post(**params)
        return import_response_list.value

    async def get_attachment(
            self,
            stream_id: str,
            message_id: str,
            attachment_id: str
    ) -> str:
        """Downloads the attachment body by the stream ID, message ID and attachment ID.
        See: `Attachment <https://developers.symphony.com/restapi/reference#attachment>`_

        :param stream_id: The stream ID where to look for the attachment.
        :param message_id: The ID of the message containing the attachment.
        :param attachment_id: The ID of the attachment

        :return: a byte array of attachment encoded in base 64.

        """
        params = {
            "sid": stream_id,
            "file_id": attachment_id,
            "message_id": message_id,
            "session_token": await self._auth_session.session_token,
            "key_manager_token": await self._auth_session.key_manager_token
        }
        return await self._attachment_api.v1_stream_sid_attachment_get(**params)

    async def get_message_status(
            self,
            message_id: str
    ) -> MessageStatus:
        """Get the status of a particular message, i.e the list of users who the message was sent to,
        delivered to and the list of users who read the message.
        See: `Message Status <https://developers.symphony.com/restapi/reference#message-status>`_

        :param message_id: MessageId the ID of the message to be checked

        :return: Status of the given message

        """
        params = {
            "mid": message_id,
            "session_token": await self._auth_session.session_token
        }
        return await self._message_api.v1_message_mid_status_get(**params)

    @retry
    async def get_attachment_types(self) -> List[str]:
        """Retrieves a list of supported file extensions for attachments.
        See: `Attachment Types <https://developers.symphony.com/restapi/reference#attachment-types>`_

        :return: a list of String containing all allowed file extensions for attachments.

        """
        params = {
            "session_token": await self._auth_session.session_token
        }
        type_list = await self._pod_api.v1_files_allowed_types_get(**params)
        return type_list.value

    @retry
    async def get_message(
            self,
            message_id: str
    ) -> V4Message:
        """Retrieves the details of a message given its message ID.
        See: `Get Message <https://developers.symphony.com/restapi/reference#get-message-v1>`_

        :param message_id: MessageId the ID of the message to be retrieved.

        :return: a V4Message containing the message's details.

        """
        params = {
            "id": message_id,
            "session_token": await self._auth_session.session_token,
            "key_manager_token": await self._auth_session.key_manager_token
        }
        return await self._messages_api.v1_message_id_get(**params)

    @retry
    async def list_attachments(
            self,
            stream_id: str,
            since: int = None,
            to: int = None,
            limit: int = 50,
            sort_dir: str = "ASC"
    ) -> List[StreamAttachmentItem]:
        """List attachments in a particular stream.
        See: `List Attachments <https://developers.symphony.com/restapi/reference#list-attachments>`_

        :param stream_id: The stream ID where to look for the attachments
        :param since: Timestamp of the first required attachment.
        :param to: Timestamp of the last required attachment.
        :param limit: Maximum number of attachments to return.
                    This optional value defaults to 50 and should be between 0 and 100.
        :param sort_dir: Attachment date sort direction : ASC or DESC. Default: ASC.

        :return: the list of attachments in the stream.

        """
        params = {
            "sid": stream_id,
            "session_token": await self._auth_session.session_token,
            "limit": limit,
            "sort_dir": sort_dir
        }
        if since is not None:
            params["since"] = since
        if to is not None:
            params["to"] = to
        attachment_list = await self._streams_api.v1_streams_sid_attachments_get(**params)
        return attachment_list.value

    @retry
    async def list_message_receipts(
            self,
            message_id: str
    ) -> MessageReceiptDetailResponse:
        """Fetches receipts details from a specific message.
        See: `List Message Receipts <https://developers.symphony.com/restapi/reference#list-message-receipts>`_

        :param message_id: MessageId the ID of the message to get receipt details from.

        :return:a MessageReceiptDetailResponse object holding all receipt information.

        """
        params = {
            "message_id": message_id,
            "session_token": await self._auth_session.session_token
        }
        return await self._default_api.v1_admin_messages_message_id_receipts_get(**params)

    @retry
    async def get_message_relationships(
            self,
            message_id: str
    ) -> MessageMetadataResponse:
        """Gets the message metadata relationship.
        This API allows users to track the relationship between a message and all the forwards and replies of that
        message.
        See: `Message Metadata <https://developers.symphony.com/restapi/reference#message-metadata-relationship>`_


        :param message_id: the ID of the message to get relationships from.
        :return: a MessageMetadataResponse object holding information about the current message relationships (parent,
            replies, forwards and form replies).
        """
        params = {
            "message_id": message_id,
            "session_token": await self._auth_session.session_token,
            "user_agent": ""
        }
        return await self._default_api.v1_admin_messages_message_id_metadata_relationships_get(**params)

    @retry
    async def search_messages(self, query: MessageSearchQuery, sort_dir: str = "desc", skip: int = 0,
                              limit: int = 50) -> List[V4Message]:
        """Searches for messages in the context of a specified user, given an argument-based query and pagination
        attributes (skip and limit parameters).
        See: `Message Search (using POST) <https://developers.symphony.com/restapi/reference#message-search-post>`_

        :param query: The search query arguments
        :param sort_dir: Sorting direction for response. Possible values are desc (default) and asc.
        :param skip: Number of messages to skip. Default: 0
        :param limit: Maximum number of messages to return. Default: 50
        :return: The list of matching messages in the stream
        """
        MessageService._validate_message_search_query(query)
        params = {
            "session_token": await self._auth_session.session_token,
            "key_manager_token": await self._auth_session.key_manager_token,
            "query": query,
            "sort_dir": sort_dir,
            "skip": skip,
            "limit": limit
        }
        message_list = await self._messages_api.v1_message_search_post(**params)
        return message_list.value  # endpoint returns empty list when no values found

    async def search_all_messages(self, query: MessageSearchQuery, sort_dir: str = "desc", chunk_size: int = 50,
                                  max_number: int = None) -> AsyncGenerator[V4Message, None]:
        """Searches for messages in the context of a specified user, given an argument-based query.
        See: `Message Search (using POST) <https://developers.symphony.com/restapi/reference#message-search-post>`_

        :param query: The search query arguments
        :param sort_dir: Sorting direction for response. Possible values are desc (default) and asc.
        :param chunk_size: the maximum number of elements to retrieve in one underlying HTTP call
        :param max_number: the total maximum number of elements to retrieve
        :return: an asynchronous generator of matching messages
        """

        async def search_messages_one_page(skip, limit):
            return await self.search_messages(query, sort_dir, skip, limit)

        return offset_based_pagination(search_messages_one_page, chunk_size, max_number)

    @retry
    async def update_message(self, stream_id: str, message_id: str, message: Union[str, Message], data=None,
                             version: str = "") -> V4Message:
        """Update an existing message. The existing message must be a valid social message, that has not been deleted.
        See: `Update Message <https://developers.symphony.com/restapi/reference#update-message-v4>`_

        :param stream_id: The ID of the stream where the message is being updated.
        :param message_id: The ID of the message that is being updated.
        :param message: a :py:class:`Message` instance or a string containing the MessageML content to be sent.
          If it is a :py:class:`Message` instance, other parameters will be ignored.
          If it is a string, ``<messageML>`` tags can be omitted.
        :param data: an object (e.g. dict) that will be serialized into JSON using ``json.dumps``.
        :param version: Optional message version in the format "major.minor".
          If empty, defaults to the latest supported version.

        :return: a V4Message object containing the details of the updated message.
        """
        message_object = message if isinstance(message, Message) else Message(content=message, data=data, version=version)

        params = {
            "sid": stream_id,
            "mid": message_id,
            "session_token": await self._auth_session.session_token,
            "key_manager_token": await self._auth_session.key_manager_token,
            "message": message_object.content,
            "data": message_object.data,
            "version": message_object.version
        }
        return await self._messages_api.v4_stream_sid_message_mid_update_post(**params)

    @staticmethod
    def _validate_message_search_query(query: MessageSearchQuery):
        # Check streamType value among accepted ones if specified
        if query.stream_type is not None and query.stream_type not in ["CHAT", "IM", "MIM", "ROOM", "POST"]:
            raise ValueError(f"Wrong stream type {query.stream_type}. "
                             f"Accepted values are: CHAT (1-1 instant messages and multi-party instant messages), "
                             f"IM (1-1 instant message), MIM (multi-party instant message), "
                             f"ROOM or POST (user profile wall posts)")

        # Text queries require streamId to be provided
        if query.text is not None and query.stream_id is None:
            raise ValueError("Message text queries require a stream_id to be provided.")
