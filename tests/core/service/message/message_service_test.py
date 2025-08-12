import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.service.message.model import Message
from symphony.bdk.core.service.message.multi_attachments_messages_api import (
    MultiAttachmentsMessagesApi,
)
from symphony.bdk.gen.agent_api.attachments_api import AttachmentsApi
from symphony.bdk.gen.agent_model.message_search_query import MessageSearchQuery
from symphony.bdk.gen.agent_model.v4_import_response_list import V4ImportResponseList
from symphony.bdk.gen.agent_model.v4_imported_message import V4ImportedMessage
from symphony.bdk.gen.agent_model.v4_message import V4Message
from symphony.bdk.gen.agent_model.v4_message_blast_response import V4MessageBlastResponse
from symphony.bdk.gen.agent_model.v4_message_list import V4MessageList
from symphony.bdk.gen.api_client import ApiClient, Configuration
from symphony.bdk.gen.pod_api.default_api import DefaultApi
from symphony.bdk.gen.pod_api.message_api import MessageApi
from symphony.bdk.gen.pod_api.message_suppression_api import MessageSuppressionApi
from symphony.bdk.gen.pod_api.pod_api import PodApi
from symphony.bdk.gen.pod_api.streams_api import StreamsApi
from symphony.bdk.gen.pod_model.message_metadata_response import MessageMetadataResponse
from symphony.bdk.gen.pod_model.message_receipt_detail_response import MessageReceiptDetailResponse
from symphony.bdk.gen.pod_model.message_status import MessageStatus
from symphony.bdk.gen.pod_model.message_suppression_response import MessageSuppressionResponse
from symphony.bdk.gen.pod_model.stream_attachment_response import StreamAttachmentResponse
from symphony.bdk.gen.pod_model.string_list import StringList
from tests.core.config import minimal_retry_config
from tests.utils.resource_utils import deserialize_object, get_deserialized_object_from_resource


@pytest.fixture(name="auth_session")
def fixture_auth_session():
    auth_session = AuthSession(None)
    auth_session.session_token = "session_token"
    auth_session.key_manager_token = "km_token"
    return auth_session


@pytest.fixture(name="mocked_api_client")
def fixture_mocked_api_client():
    api_client = MagicMock(ApiClient)
    api_client.call_api = AsyncMock()
    api_client.configuration = Configuration()
    return api_client


@pytest.fixture(name="message_service")
def fixture_message_service(mocked_api_client, auth_session):
    service = MessageService(
        MultiAttachmentsMessagesApi(mocked_api_client),
        MessageApi(mocked_api_client),
        MessageSuppressionApi(mocked_api_client),
        StreamsApi(mocked_api_client),
        PodApi(mocked_api_client),
        AttachmentsApi(mocked_api_client),
        DefaultApi(mocked_api_client),
        auth_session,
        minimal_retry_config(),
    )
    return service


@pytest.mark.asyncio
async def test_list_messages(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        V4MessageList, "message_response/list_messages.json"
    )
    messages_list = await message_service.list_messages("stream_id")

    assert len(messages_list) == 1
    assert messages_list[0].message_id == "test-message1"


@pytest.mark.asyncio
async def test_send_message(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        V4Message, "message_response/message.json"
    )
    message = await message_service.send_message("stream_id", "test_message")

    assert message.message_id == "-AANBHKtUC-2q6_0WSjBGX___pHnSfBKdA"
    assert message.user.user_id == 7078106482890


@pytest.mark.asyncio
async def test_send_simple_message(message_service):
    message_service._send_message = AsyncMock(
        return_value=get_deserialized_object_from_resource(
            V4Message, "message_response/message.json"
        )
    )
    message = "<messageML>Hello</messageML>"
    stream_id = "stream_id"

    await message_service.send_message(stream_id, message)

    message_service._send_message.assert_called_once_with(stream_id, message, "", "", [], [])


@pytest.mark.asyncio
async def test_send_simple_message_without_mml_tags(message_service):
    message_service._send_message = AsyncMock(
        return_value=get_deserialized_object_from_resource(
            V4Message, "message_response/message.json"
        )
    )
    stream_id = "stream_id"

    await message_service.send_message(stream_id, "Hello")

    message_service._send_message.assert_called_once_with(
        stream_id, "<messageML>Hello</messageML>", "", "", [], []
    )


@pytest.mark.asyncio
async def test_send_message_with_data(message_service):
    message_service._send_message = AsyncMock(
        return_value=get_deserialized_object_from_resource(
            V4Message, "message_response/message.json"
        )
    )
    message = "<messageML>Hello</messageML>"
    stream_id = "stream_id"
    data = ["foo", {"bar": ("baz", 1.0, 2)}]
    json_data = json.dumps(data)

    await message_service.send_message(stream_id, message, data)

    message_service._send_message.assert_called_once_with(stream_id, message, json_data, "", [], [])


@pytest.mark.asyncio
async def test_send_complex_message(message_service):
    message_service._send_message = AsyncMock(
        return_value=get_deserialized_object_from_resource(
            V4Message, "message_response/message.json"
        )
    )
    stream_id = "stream_id"
    content = "<messageML>Hello</messageML>"
    data = ["foo", {"bar": ("baz", 1.0, 2)}]
    json_data = json.dumps(data)
    version = "2.0"
    attachment = "attachment"
    preview = "preview"
    message = Message(
        content=content, data=data, attachments=[(attachment, preview)], version=version
    )

    await message_service.send_message(stream_id, message)

    message_service._send_message.assert_called_once_with(
        stream_id, content, json_data, version, [attachment], [preview]
    )


@pytest.mark.asyncio
async def test_blast_message(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        V4MessageBlastResponse, "message_response/blast_message.json"
    )
    blast_message = await message_service.blast_message(
        ["stream_id1", "stream_id2"], "test_message"
    )

    assert len(blast_message.messages) == 2
    assert blast_message.messages[0].message_id == "-AANBHKtUC-2q6_0WSjBGX___pHnSfBKdA-1"
    assert blast_message.messages[1].message_id == "-AANBHKtUC-2q6_0WSjBGX___pHnSfBKdA-2"


@pytest.mark.asyncio
async def test_blast_simple_message(message_service):
    blast_message_response = get_deserialized_object_from_resource(
        V4MessageBlastResponse, "message_response/blast_message.json"
    )
    message_service._blast_message = AsyncMock(return_value=blast_message_response)
    stream_ids = ["sid1", "sid2"]
    message = "<messageML>Hello</messageML>"

    await message_service.blast_message(stream_ids, message)

    message_service._blast_message.assert_called_once_with(stream_ids, message, "", "", [], [])


@pytest.mark.asyncio
async def test_blast_simple_message_without_mml_tags(message_service):
    blast_message_response = get_deserialized_object_from_resource(
        V4MessageBlastResponse, "message_response/blast_message.json"
    )
    message_service._blast_message = AsyncMock(return_value=blast_message_response)
    stream_ids = ["sid1", "sid2"]
    await message_service.blast_message(stream_ids, "Hello")

    message_service._blast_message.assert_called_once_with(
        stream_ids, "<messageML>Hello</messageML>", "", "", [], []
    )


@pytest.mark.asyncio
async def test_blast_message_with_data(message_service):
    blast_message_response = get_deserialized_object_from_resource(
        V4MessageBlastResponse, "message_response/blast_message.json"
    )
    message_service._blast_message = AsyncMock(return_value=blast_message_response)
    stream_ids = ["sid1", "sid2"]
    message = "<messageML>Hello</messageML>"
    data = ["foo", {"bar": ("baz", 1.0, 2)}]
    json_data = json.dumps(data)

    await message_service.blast_message(stream_ids, message, data)

    message_service._blast_message.assert_called_once_with(
        stream_ids, message, json_data, "", [], []
    )


@pytest.mark.asyncio
async def test_blast_complex_message(message_service):
    blast_message_response = get_deserialized_object_from_resource(
        V4MessageBlastResponse, "message_response/blast_message.json"
    )
    message_service._blast_message = AsyncMock(return_value=blast_message_response)
    stream_ids = ["sid1", "sid2"]
    content = "<messageML>Hello</messageML>"
    data = ["foo", {"bar": ("baz", 1.0, 2)}]
    version = "2.0"
    attachment = "attachment"
    preview = "preview"
    json_data = json.dumps(data)

    message = Message(
        content=content, data=data, attachments=[(attachment, preview)], version=version
    )

    await message_service.blast_message(stream_ids, message)

    message_service._blast_message.assert_called_once_with(
        stream_ids, content, json_data, version, [attachment], [preview]
    )


@pytest.mark.asyncio
async def test_import_message(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = deserialize_object(
        V4ImportResponseList,
        "["
        "   {"
        '       "messageId": "FjSY1y3L",  '
        '       "originatingSystemId": "AGENT_SDK",'
        '       "originalMessageId": "M2"'
        "   }"
        "]",
    )

    import_response = await message_service.import_messages(
        [
            V4ImportedMessage(
                message="test_message",
                intended_message_timestamp=1433045622000,
                intended_message_from_user_id=7215545057281,
                originating_system_id="fooChat",
                stream_id="Z3oQRAZGTCNl5KjiUH2G1n___qr9lLT8dA",
            )
        ]
    )

    assert len(import_response) == 1
    assert import_response[0].message_id == "FjSY1y3L"
    assert import_response[0].originating_system_id == "AGENT_SDK"


@pytest.mark.asyncio
async def test_get_attachment(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = "attachment-string"

    attachment = await message_service.get_attachment("stream-id", "message-id", "attachment-id")

    assert attachment == "attachment-string"


@pytest.mark.asyncio
async def test_suppress_message(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        MessageSuppressionResponse, "message_response/supress_message.json"
    )
    suppress_response = await message_service.suppress_message("test-message-id")

    assert suppress_response.message_id == "test-message-id"
    assert suppress_response.suppression_date == 1461565603191


@pytest.mark.asyncio
async def test_get_message_status(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        MessageStatus, "message_response/message_status.json"
    )

    message_status = await message_service.get_message_status("test-message-id")

    assert message_status.author.user_id == "7078106103901"
    assert len(message_status.read) == 2
    assert len(message_status.sent) == 1


@pytest.mark.asyncio
async def test_get_attachment_types(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = deserialize_object(
        StringList, '[   ".bmp",   ".doc",   ".png",   ".mpeg"]'
    )

    attachment_types = await message_service.get_attachment_types()

    assert len(attachment_types) == 4
    assert attachment_types[0] == ".bmp"


@pytest.mark.asyncio
async def test_get_message(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        V4Message, "message_response/message.json"
    )

    message = await message_service.get_message("-AANBHKtUC-2q6_0WSjBGX___pHnSfBKdA")

    assert message.message_id == "-AANBHKtUC-2q6_0WSjBGX___pHnSfBKdA"
    assert message.timestamp == 1572372615137
    assert message.user.user_id == 7078106482890


@pytest.mark.asyncio
async def test_list_attachments(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        StreamAttachmentResponse, "message_response/list_attachments.json"
    )

    attachments = await message_service.list_attachments("stream_id")

    assert len(attachments) == 2
    assert attachments[0].message_id == "PYLHNm/1K6ppeOpj+FbQ"
    assert attachments[1].file_id == "internal_14362370637825%2FeM6zGAILWFakDObCwMANrw%3D%3D"


@pytest.mark.asyncio
async def test_message_receipts(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        MessageReceiptDetailResponse, "message_response/message_receipts.json"
    )

    message_receipts = await message_service.list_message_receipts("test-message-id")

    assert message_receipts.creator.id == 7215545058329
    assert message_receipts.stream.id == "lFpyw0ATFmji+Cc/cSzbk3///pZkWpe1dA=="
    assert message_receipts.message_receipt_detail[0].user.id == 7215545058329


@pytest.mark.asyncio
async def test_get_message_relationships(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        MessageMetadataResponse, "message_response/message_relationships.json"
    )

    message_relationships = await message_service.get_message_relationships(
        "TYgOZ65dVsu3SeK7u2YdfH///o6fzBu"
    )

    assert message_relationships.message_id == "TYgOZ65dVsu3SeK7u2YdfH///o6fzBu"
    assert message_relationships.parent.message_id == "/rbLQW5UHKZffM0FlLO2rn///o6vTck"
    assert message_relationships.parent.relationship_type == "REPLY"


@pytest.mark.asyncio
async def test_search_messages_with_hashtag(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        V4MessageList, "message_response/list_messages.json"
    )

    messages = await message_service.search_messages(MessageSearchQuery(hashtag="tag"))
    assert len(messages) == 1
    assert messages[0].message_id == "test-message1"


@pytest.mark.asyncio
@pytest.mark.parametrize("stream_type", ["CHAT", "IM", "MIM", "ROOM", "POST"])
async def test_search_messages_with_valid_stream_type(
    mocked_api_client, message_service, stream_type
):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        V4MessageList, "message_response/list_messages.json"
    )

    messages = await message_service.search_messages(MessageSearchQuery(stream_type=stream_type))
    assert len(messages) == 1
    assert messages[0].message_id == "test-message1"


@pytest.mark.asyncio
async def test_search_messages_with_invalid_stream_type(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        V4MessageList, "message_response/list_messages.json"
    )

    with pytest.raises(ValueError):
        await message_service.search_messages(MessageSearchQuery(stream_type="invalid"))


@pytest.mark.asyncio
async def test_search_messages_with_text_and_sid(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        V4MessageList, "message_response/list_messages.json"
    )

    messages = await message_service.search_messages(
        MessageSearchQuery(text="some text", stream_id="sid")
    )
    assert len(messages) == 1
    assert messages[0].message_id == "test-message1"


@pytest.mark.asyncio
async def test_search_messages_with_text_and_no_sid(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        V4MessageList, "message_response/list_messages.json"
    )

    with pytest.raises(ValueError):
        await message_service.search_messages(MessageSearchQuery(text="some text"))


@pytest.mark.asyncio
@pytest.mark.parametrize("stream_type", ["CHAT", "IM", "MIM", "ROOM", "POST"])
async def test_search_messages_with_stream_type_text_and_sid(
    mocked_api_client, message_service, stream_type
):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        V4MessageList, "message_response/list_messages.json"
    )

    messages = await message_service.search_messages(
        MessageSearchQuery(text="some text", stream_id="sid", stream_type=stream_type)
    )
    assert len(messages) == 1
    assert messages[0].message_id == "test-message1"


@pytest.mark.asyncio
@pytest.mark.parametrize("stream_type", ["CHAT", "IM", "MIM", "ROOM", "POST"])
async def test_search_messages_with_stream_type_text_and_no_sid(
    mocked_api_client, message_service, stream_type
):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        V4MessageList, "message_response/list_messages.json"
    )

    with pytest.raises(ValueError):
        await message_service.search_messages(
            MessageSearchQuery(text="some text", stream_type=stream_type)
        )


@pytest.mark.asyncio
async def test_search_all_messages(mocked_api_client, message_service):
    mocked_api_client.call_api.side_effect = [
        get_deserialized_object_from_resource(V4MessageList, "message_response/list_messages.json"),
        V4MessageList(value=[]),
    ]
    chunk_size = 1

    message_generator = await message_service.search_all_messages(
        MessageSearchQuery(hashtag="tag"), chunk_size=chunk_size
    )
    messages = [m async for m in message_generator]
    assert len(messages) == 1
    assert messages[0].message_id == "test-message1"

    assert mocked_api_client.call_api.call_count == 2


@pytest.mark.asyncio
async def test_update_message(mocked_api_client, message_service):
    mocked_api_client.call_api.return_value = get_deserialized_object_from_resource(
        V4Message, "message_response/update_message.json"
    )
    message = await message_service.update_message(
        "stream_id", "message_id", "test_message", "data", "version"
    )

    assert message.message_id == "ikCBeVCgQT876veVzQzOV3___oNI6f8obQ"
    assert message.user.user_id == 11338713662703
    assert message.silent
