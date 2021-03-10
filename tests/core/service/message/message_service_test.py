from unittest.mock import MagicMock, AsyncMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.service.message.multi_attachments_messages_api import MultiAttachmentsMessagesApi
from symphony.bdk.gen.agent_api.attachments_api import AttachmentsApi
from symphony.bdk.gen.agent_model.v4_imported_message import V4ImportedMessage
from symphony.bdk.gen.api_client import ApiClient, Configuration
from symphony.bdk.gen.pod_api.default_api import DefaultApi
from symphony.bdk.gen.pod_api.message_api import MessageApi
from symphony.bdk.gen.pod_api.message_suppression_api import MessageSuppressionApi
from symphony.bdk.gen.pod_api.pod_api import PodApi
from symphony.bdk.gen.pod_api.streams_api import StreamsApi
from tests.utils.resource_utils import object_from_json_relative_path, object_from_json


@pytest.fixture(name='auth_session')
def fixture_auth_session():
    auth_session = AuthSession(None)
    auth_session.session_token = 'session_token'
    auth_session.key_manager_token = 'km_token'
    return auth_session


@pytest.fixture(name='api_client')
def fixture_api_client():
    api_client = MagicMock(ApiClient)
    api_client.call_api = AsyncMock()
    api_client.configuration = Configuration()
    return api_client


@pytest.fixture(name='message_service')
def fixture_message_service(api_client, auth_session):
    service = MessageService(
        MultiAttachmentsMessagesApi(api_client),
        MessageApi(api_client),
        MessageSuppressionApi(api_client),
        StreamsApi(api_client),
        PodApi(api_client),
        AttachmentsApi(api_client),
        DefaultApi(api_client),
        auth_session
    )
    return service


@pytest.mark.asyncio
async def test_list_messages(api_client, message_service):
    api_client.call_api.return_value = object_from_json_relative_path('message_response/list_messages.json')
    messages_list = await message_service.list_messages('stream_id')

    assert len(messages_list) == 1
    assert messages_list[0].messageId == 'test-message1'


@pytest.mark.asyncio
async def test_send_message(api_client, message_service):
    api_client.call_api.return_value = object_from_json_relative_path('message_response/message.json')
    message = await message_service.send_message('stream_id', 'test_message')

    assert message.messageId == '-AANBHKtUC-2q6_0WSjBGX___pHnSfBKdA'
    assert message.user.userId == 7078106482890


@pytest.mark.asyncio
async def test_blast_message(api_client, message_service):
    api_client.call_api.return_value = object_from_json_relative_path('message_response/blast_message.json')
    blast_message = await message_service.blast_message(['stream_id1', 'stream_id2'], 'test_message')

    assert len(blast_message.messages) == 2
    assert blast_message.messages[0].messageId == '-AANBHKtUC-2q6_0WSjBGX___pHnSfBKdA-1'
    assert blast_message.messages[1].messageId == '-AANBHKtUC-2q6_0WSjBGX___pHnSfBKdA-2'


@pytest.mark.asyncio
async def test_import_message(api_client, message_service):
    api_client.call_api.return_value = object_from_json(
        '{"value": ['
        '   {'
        '       "messageId": "FjSY1y3L",  '
        '       "originatingSystemId": "AGENT_SDK",'
        '       "originalMessageId": "M2"'
        '   }'
        ']}')

    import_response = await message_service.import_messages([V4ImportedMessage(
        message='test_message',
        intended_message_timestamp=1433045622000,
        intended_message_from_user_id=7215545057281,
        originating_system_id='fooChat',
        stream_id='Z3oQRAZGTCNl5KjiUH2G1n___qr9lLT8dA'
    )])

    assert len(import_response) == 1
    assert import_response[0].messageId == 'FjSY1y3L'
    assert import_response[0].originatingSystemId == 'AGENT_SDK'


@pytest.mark.asyncio
async def test_get_attachment(api_client, message_service):
    api_client.call_api.return_value = 'attachment-string'

    attachment = await message_service.get_attachment('stream-id', 'message-id', 'attachment-id')

    assert attachment == 'attachment-string'


@pytest.mark.asyncio
async def test_suppress_message(api_client, message_service):
    api_client.call_api.return_value = object_from_json(
        '{'
        '   "messageId": "test-message-id",'
        '   "suppressed": true,'
        '   "suppressionDate": 1461565603191'
        '}')
    suppress_response = await message_service.suppress_message('test-message-id')

    assert suppress_response.messageId == 'test-message-id'
    assert suppress_response.suppressionDate == 1461565603191


@pytest.mark.asyncio
async def test_get_message_status(api_client, message_service):
    api_client.call_api.return_value = object_from_json_relative_path('message_response/message_status.json')
    message_status = await message_service.get_message_status('test-message-id')

    assert message_status.author.userId == '7078106103901'
    assert len(message_status.read) == 2
    assert len(message_status.sent) == 1


@pytest.mark.asyncio
async def test_get_attachment_types(api_client, message_service):
    api_client.call_api.return_value = object_from_json(
        '{"value": ['
        '   ".bmp",'
        '   ".doc",'
        '   ".png",'
        '   ".mpeg"'
        ']}'
    )
    attachment_types = await message_service.get_attachment_types()

    assert len(attachment_types) == 4
    assert attachment_types[0] == '.bmp'


@pytest.mark.asyncio
async def test_get_message(api_client, message_service):
    api_client.call_api.return_value = object_from_json_relative_path('message_response/message.json')
    message = await message_service.get_message('-AANBHKtUC-2q6_0WSjBGX___pHnSfBKdA')

    assert message.messageId == '-AANBHKtUC-2q6_0WSjBGX___pHnSfBKdA'
    assert message.timestamp == 1572372615137
    assert message.user.userId == 7078106482890


@pytest.mark.asyncio
async def test_list_attachments(api_client, message_service):
    api_client.call_api.return_value = object_from_json_relative_path('message_response/list_attachments.json')
    attachments = await message_service.list_attachments('stream_id')

    assert len(attachments) == 2
    assert attachments[0].messageId == 'PYLHNm/1K6p...peOpj+FbQ'
    assert attachments[1].fileId == 'internal_14362370637825%2FeM6zGAILWFakDObCwMANrw%3D%3D'


@pytest.mark.asyncio
async def test_message_receipts(api_client, message_service):
    api_client.call_api.return_value = object_from_json_relative_path('message_response/message_receipts.json')
    message_receipts = await message_service.list_message_receipts('test-message-id')

    assert message_receipts.creator.id == 7215545058329
    assert message_receipts.stream.id == 'lFpyw0ATFmji+Cc/cSzbk3///pZkWpe1dA=='
    assert message_receipts.MessageReceiptDetail[0].user.id == 7215545058329


@pytest.mark.asyncio
async def test_get_message_relationships(api_client, message_service):
    api_client.call_api.return_value = object_from_json(
        '{ '
        '   "messageId": "TYgOZ65dVsu3SeK7u2YdfH///o6fzBu",'
        '   "parent": {'
        '       "messageId": "/rbLQW5UHKZffM0FlLO2rn///o6vTck",'
        '       "relationshipType": "REPLY"    '
        '   },'
        '   "replies": [],'
        '   "forwards": [],'
        '   "formReplies": []'
        '}'
    )
    message_relationships = await message_service.get_message_relationships('TYgOZ65dVsu3SeK7u2YdfH///o6fzBu')

    assert message_relationships.messageId == 'TYgOZ65dVsu3SeK7u2YdfH///o6fzBu'
    assert message_relationships.parent.messageId == '/rbLQW5UHKZffM0FlLO2rn///o6vTck'
    assert message_relationships.parent.relationshipType == 'REPLY'
