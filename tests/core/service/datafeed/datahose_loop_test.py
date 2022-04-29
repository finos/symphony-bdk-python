import asyncio
from unittest.mock import MagicMock, AsyncMock

import pytest

from symphony.bdk.core.service.datafeed.datahose_loop import DatahoseLoop
from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import RealTimeEvent
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.gen import ApiClient
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_event import V4Event
from symphony.bdk.gen.agent_model.v4_payload import V4Payload
from symphony.bdk.gen.agent_model.v4_user import V4User
from symphony.bdk.gen.pod_model.user_v2 import UserV2
from symphony.bdk.gen.agent_model.v5_events_read_body import V5EventsReadBody
from symphony.bdk.gen.agent_model.v5_event_list import V5EventList
from tests.core.config import minimal_retry_config
from tests.utils.resource_utils import get_config_resource_filepath


ACK_ID = "ack_id"


class EventsMock:
    def __init__(self, events, ack_id=ACK_ID):
        self.events = events
        self.ack_id = ack_id


@pytest.fixture(name="auth_session")
def fixture_auth_session():
    auth_session = AuthSession(None)
    auth_session.session_token = "session_token"
    auth_session.key_manager_token = "km_token"
    return auth_session


@pytest.fixture(name="config")
def fixture_config():
    config = BdkConfigLoader.load_from_file(get_config_resource_filepath("config.yaml"))
    config.datahose.retry = minimal_retry_config()
    config.datahose.tag = "TEST_TAG"
    config.datahose.filters = ["SOCIALMESSAGE"]
    return config


@pytest.fixture(name="datafeed_api")
def fixture_datafeed_api():
    datafeed_api = MagicMock(DatafeedApi)
    datafeed_api.api_client = MagicMock(ApiClient)
    datafeed_api.list_datafeed = AsyncMock()
    datafeed_api.create_datafeed = AsyncMock()
    datafeed_api.read_datafeed = AsyncMock()
    datafeed_api.read_events = AsyncMock()
    datafeed_api.delete_datafeed = AsyncMock()
    return datafeed_api


@pytest.fixture(name="session_service")
def fixture_session_service():
    session_service = AsyncMock()
    session_service.get_session.return_value = UserV2(id=12345)
    return session_service


@pytest.fixture(name="datahose_loop")
def fixture_datahose_loop(datafeed_api, session_service, auth_session, config):
    datahose_loop = DatahoseLoop(datafeed_api, session_service, auth_session, config)

    class RealTimeEventListenerImpl(RealTimeEventListener):

        async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
            await datahose_loop.stop()

    datahose_loop.subscribe(RealTimeEventListenerImpl())
    return datahose_loop


@pytest.fixture(name="initiator")
def fixture_initiator():
    return V4Initiator(user=V4User(username="username"))


@pytest.fixture(name="message_sent")
def fixture_message_sent(initiator):
    return V4Event(type=RealTimeEvent.MESSAGESENT.name,
                   payload=V4Payload(message_sent=V4MessageSent()),
                   initiator=initiator)


@pytest.fixture(name="message_sent_event")
def fixture_message_sent_event(message_sent):
    return EventsMock([message_sent], "test_events_ack_id")


@pytest.fixture(name="read_events_side_effect")
def fixture_read_events_side_effect(message_sent_event):
    async def read_events(**kwargs):
        await asyncio.sleep(0.001)  # to force the switching of tasks
        events_list = V5EventList()
        events_list.ack_id = "test_events_ack_id"
        events_list.events = [message_sent_event]
        return events_list

    return read_events


@pytest.mark.asyncio
async def test_start(datahose_loop, datafeed_api, message_sent_event):
    datafeed_api.read_events.return_value = message_sent_event
    body = V5EventsReadBody(type="datahose", tag="TEST_TAG",
                            filters=["SOCIALMESSAGE"], ack_id="")
    await datahose_loop.start()

    datafeed_api.read_events.assert_called_with(
        session_token="session_token",
        key_manager_token="km_token",
        body=body
    )

    assert datahose_loop._ack_id == "test_events_ack_id"


@pytest.mark.asyncio
async def test_start_already_started_datahose_loop_should_throw_error(datahose_loop):
    datahose_loop._running = True
    with pytest.raises(RuntimeError, match="The datahose service is already started"):
        await datahose_loop.start()
