import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import RealTimeEvent
from symphony.bdk.gen import ApiClient
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.gen.agent_model.v4_event import V4Event
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message import V4Message
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_payload import V4Payload
from symphony.bdk.gen.agent_model.v4_user import V4User
from symphony.bdk.gen.pod_model.user_v2 import UserV2


class EventsMock:
    def __init__(self, events, ack_id="ack_id"):
        self.events = events
        self.ack_id = ack_id


@pytest.fixture(name="initiator_userid", scope="module")
def fixture_initiator_userid():
    return V4Initiator(user=V4User(user_id=67890))


@pytest.fixture(name="initiator_username")
def fixture_initiator_username():
    return V4Initiator(user=V4User(username="username"))


@pytest.fixture(name="auth_session")
def fixture_auth_session():
    auth_session = AuthSession(None)
    auth_session.session_token = "session_token"
    auth_session.key_manager_token = "km_token"
    return auth_session


@pytest.fixture(name="session_service")
def fixture_session_service():
    session_service = AsyncMock()
    session_service.get_session.return_value = UserV2(id=12345)
    return session_service


@pytest.fixture(name="datafeed_api")
def fixture_datafeed_api():
    datafeed_api = MagicMock(DatafeedApi)
    datafeed_api.api_client = MagicMock(ApiClient)
    datafeed_api.v4_datafeed_create_post = AsyncMock()
    datafeed_api.v4_datafeed_id_read_get = AsyncMock()
    return datafeed_api


@pytest.fixture(name="message_sent_v4_event")
def fixture_message_sent_v4_event(initiator_userid):
    payload = V4Payload(message_sent=V4MessageSent(message=V4Message(attachments=[], message="message")))
    return V4Event(type=RealTimeEvent.MESSAGESENT.name, payload=payload, initiator=initiator_userid)


@pytest.fixture(name="message_sent_events_mock")
def fixture_message_sent_events_mock(message_sent):
    return EventsMock([message_sent], "test_events_ack_id")