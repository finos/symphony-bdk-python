import asyncio
from unittest.mock import MagicMock, AsyncMock, call

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import RealTimeEvent
from symphony.bdk.core.service.datafeed.datafeed_loop_v2 import DatafeedLoopV2
from symphony.bdk.core.service.datafeed.exception import EventError
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.gen import ApiClient, ApiException
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.gen.agent_model.ack_id import AckId
from symphony.bdk.gen.agent_model.v4_event import V4Event
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_payload import V4Payload
from symphony.bdk.gen.agent_model.v4_user import V4User
from symphony.bdk.gen.agent_model.v5_datafeed import V5Datafeed
from symphony.bdk.gen.agent_model.v5_datafeed_create_body import V5DatafeedCreateBody
from symphony.bdk.gen.pod_model.user_v2 import UserV2
from tests.core.config import minimal_retry_config, minimal_retry_config_with_attempts
from tests.utils.resource_utils import get_config_resource_filepath

ACK_ID = "ack_id"
BOT_USER = "youbot"

SLEEP_SECONDS = 0.0001


class EventsMock:
    def __init__(self, events, ack_id=ACK_ID):
        self.events = events
        self.ack_id = ack_id


def read_df_function(event_payload):
    async def read_df(**kwargs):
        await asyncio.sleep(SLEEP_SECONDS)  # to force the switching of tasks
        return event_payload

    return read_df


async def start_and_stop_df_loop(mock_datafeed_loop):
    t = asyncio.create_task(mock_datafeed_loop.start())
    await asyncio.sleep(SLEEP_SECONDS)
    await mock_datafeed_loop.stop()
    await t


@pytest.fixture(name="auth_session")
def fixture_auth_session():
    auth_session = AuthSession(None)
    auth_session.session_token = "session_token"
    auth_session.key_manager_token = "km_token"
    return auth_session


@pytest.fixture(name="config")
def fixture_config():
    config = BdkConfigLoader.load_from_file(get_config_resource_filepath("config.yaml"))
    config.datafeed.retry = minimal_retry_config()
    config.datafeed.version = "v2"
    return config


@pytest.fixture(name="datafeed_api")
def fixture_datafeed_api():
    datafeed_api = MagicMock(DatafeedApi)
    datafeed_api.api_client = MagicMock(ApiClient)
    datafeed_api.list_datafeed = AsyncMock()
    datafeed_api.create_datafeed = AsyncMock()
    datafeed_api.read_datafeed = AsyncMock()
    datafeed_api.delete_datafeed = AsyncMock()
    return datafeed_api


@pytest.fixture(name="mock_listener")
def fixture_mock_listener():
    return AsyncMock(wraps=RealTimeEventListener())


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
    return EventsMock([message_sent])


@pytest.fixture(name="read_df_side_effect")
def fixture_read_df_side_effect(message_sent_event):
    return read_df_function(message_sent_event)


@pytest.fixture(name="session_service")
def fixture_session_service():
    session_service = AsyncMock()
    session_service.get_session.return_value = UserV2(id=12345)
    return session_service


@pytest.fixture(name="datafeed_loop")
def fixture_datafeed_loop(datafeed_api, session_service, auth_session, config):
    datafeed_loop = DatafeedLoopV2(datafeed_api, session_service, auth_session, config)

    class RealTimeEventListenerImpl(RealTimeEventListener):

        async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
            await datafeed_loop.stop()

    datafeed_loop.subscribe(RealTimeEventListenerImpl())
    return datafeed_loop


@pytest.fixture(name="mock_datafeed_loop")
def fixture_mock_datafeed_loop(datafeed_api, session_service, auth_session, config):
    datafeed_loop = DatafeedLoopV2(datafeed_api, session_service, auth_session, config)
    datafeed_loop._prepare_datafeed = AsyncMock()
    datafeed_loop._read_events = AsyncMock()
    datafeed_loop._retrieve_datafeed = AsyncMock(V5Datafeed(id="test_id"))

    return datafeed_loop


@pytest.mark.asyncio
async def test_start(datafeed_loop, datafeed_api, read_df_side_effect):
    datafeed_api.list_datafeed.return_value = []
    datafeed_api.create_datafeed.return_value = V5Datafeed(id="test_id")
    datafeed_api.read_datafeed.side_effect = read_df_side_effect

    await datafeed_loop.start()

    datafeed_api.list_datafeed.assert_called_with(
        session_token="session_token",
        key_manager_token="km_token",
        tag=BOT_USER
    )
    datafeed_api.create_datafeed.assert_called_with(
        session_token="session_token",
        key_manager_token="km_token",
        body=V5DatafeedCreateBody(tag=BOT_USER)
    )
    assert datafeed_api.read_datafeed.call_args_list[0].kwargs == {"session_token": "session_token",
                                                                   "key_manager_token": "km_token",
                                                                   "datafeed_id": "test_id",
                                                                   "ack_id": AckId(ack_id="")}
    assert datafeed_loop._datafeed_id == "test_id"
    assert datafeed_loop._ack_id == "ack_id"


@pytest.mark.asyncio
async def test_start_already_started_datafeed_v2_loop_should_throw_error(datafeed_loop):
    datafeed_loop._running = True
    with pytest.raises(RuntimeError, match="The datafeed service V2 is already started"):
        await datafeed_loop.start()


@pytest.mark.asyncio
async def test_start_datafeed_exist(datafeed_loop, datafeed_api, read_df_side_effect):
    datafeed_api.list_datafeed.return_value = [V5Datafeed(id="test_id_exist")]
    datafeed_api.read_datafeed.side_effect = read_df_side_effect

    await datafeed_loop.start()

    datafeed_api.list_datafeed.assert_called_with(
        session_token="session_token",
        key_manager_token="km_token",
        tag=BOT_USER
    )
    assert datafeed_api.read_datafeed.call_args_list[0].kwargs == {"session_token": "session_token",
                                                                   "key_manager_token": "km_token",
                                                                   "datafeed_id": "test_id_exist",
                                                                   "ack_id": AckId(ack_id="")}
    assert datafeed_loop._datafeed_id == "test_id_exist"
    assert datafeed_loop._ack_id == "ack_id"


@pytest.mark.asyncio
async def test_start_datafeed_stale_datafeed(datafeed_loop, datafeed_api, message_sent_event):
    datafeed_loop._retry_config = minimal_retry_config_with_attempts(2)
    datafeed_api.list_datafeed.return_value = [V5Datafeed(id="fault_datafeed_id")]
    datafeed_api.create_datafeed.return_value = V5Datafeed(id="test_id")

    # This is done this way because side_effect with a list containing coroutines is not behaving as expected
    async def raise_and_return_event(**kwargs):
        if raise_and_return_event.first:
            raise_and_return_event.first = False
            raise ApiException(400)
        await asyncio.sleep(SLEEP_SECONDS)  # to force the switching of tasks
        return message_sent_event

    raise_and_return_event.first = True

    datafeed_api.read_datafeed.side_effect = raise_and_return_event

    await datafeed_loop.start()

    datafeed_api.list_datafeed.assert_called_with(
        session_token="session_token",
        key_manager_token="km_token",
        tag=BOT_USER
    )

    datafeed_api.delete_datafeed.assert_called_with(
        session_token="session_token",
        key_manager_token="km_token",
        datafeed_id="fault_datafeed_id"
    )

    datafeed_api.create_datafeed.assert_called_with(
        session_token="session_token",
        key_manager_token="km_token",
        body=V5DatafeedCreateBody(tag=BOT_USER)
    )

    datafeed_api.read_datafeed.assert_has_calls([
        call(
            session_token="session_token",
            key_manager_token="km_token",
            datafeed_id="fault_datafeed_id",
            ack_id=AckId(ack_id="")
        ),
        call(
            session_token="session_token",
            key_manager_token="km_token",
            datafeed_id="test_id",
            ack_id=AckId(ack_id="")
        )
    ])

    assert datafeed_loop._datafeed_id == "test_id"
    assert datafeed_loop._ack_id == "ack_id"


@pytest.mark.asyncio
async def test_read_datafeed_no_value(mock_datafeed_loop, mock_listener):
    mock_datafeed_loop._read_events.side_effect = read_df_function(EventsMock(None))
    mock_datafeed_loop.subscribe(mock_listener)

    await start_and_stop_df_loop(mock_datafeed_loop)

    assert mock_datafeed_loop._ack_id == ACK_ID
    mock_listener.assert_not_called()


@pytest.mark.asyncio
async def test_read_datafeed_empty_list(mock_datafeed_loop, mock_listener):
    mock_datafeed_loop._read_events.side_effect = read_df_function(EventsMock([]))
    mock_datafeed_loop.subscribe(mock_listener)

    await start_and_stop_df_loop(mock_datafeed_loop)

    assert mock_datafeed_loop._ack_id == ACK_ID
    mock_listener.assert_not_called()


@pytest.mark.asyncio
async def test_read_datafeed_non_empty_list(mock_datafeed_loop, mock_listener, message_sent):
    mock_datafeed_loop._read_events.side_effect = read_df_function(EventsMock([message_sent]))
    mock_datafeed_loop.subscribe(mock_listener)

    await start_and_stop_df_loop(mock_datafeed_loop)

    assert mock_datafeed_loop._ack_id == ACK_ID
    mock_listener.on_message_sent.assert_called_with(message_sent.initiator, message_sent.payload.message_sent)


@pytest.mark.asyncio
async def test_read_datafeed_error_in_listener(mock_datafeed_loop, mock_listener, message_sent):
    mock_listener.on_message_sent.side_effect = ValueError()
    mock_datafeed_loop._read_events.side_effect = read_df_function(EventsMock([message_sent]))
    mock_datafeed_loop.subscribe(mock_listener)

    await start_and_stop_df_loop(mock_datafeed_loop)

    assert mock_datafeed_loop._ack_id == ACK_ID
    mock_listener.on_message_sent.assert_called_with(message_sent.initiator, message_sent.payload.message_sent)


@pytest.mark.asyncio
async def test_read_datafeed_event_error_in_listener(mock_datafeed_loop, mock_listener, message_sent):
    mock_listener.on_message_sent.side_effect = EventError()
    mock_datafeed_loop._read_events.side_effect = read_df_function(EventsMock([message_sent]))
    mock_datafeed_loop.subscribe(mock_listener)

    await start_and_stop_df_loop(mock_datafeed_loop)

    assert mock_datafeed_loop._ack_id == ""  # ack id not updated
    mock_listener.on_message_sent.assert_called_with(message_sent.initiator, message_sent.payload.message_sent)


@pytest.mark.asyncio
async def test_events_concurrency_within_same_read_df_chunk(mock_datafeed_loop, message_sent):
    class QueueListener(RealTimeEventListener):
        def __init__(self):
            self.queue = asyncio.Queue()
            self.count = 0

        async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
            self.count += 1
            if self.count == 1:
                await self.queue.get()
                await mock_datafeed_loop.stop()
            elif self.count == 2:
                await self.queue.put("message")

    mock_datafeed_loop._read_events.side_effect = read_df_function(EventsMock([message_sent, message_sent]))
    mock_datafeed_loop.subscribe(QueueListener())

    await mock_datafeed_loop.start()  # test no deadlock


@pytest.mark.asyncio
async def test_400_should_call_recreate_df_and_retry(datafeed_loop, datafeed_api):
    datafeed_loop._retry_config = minimal_retry_config_with_attempts(2)
    datafeed_loop.recreate_datafeed = AsyncMock()
    datafeed_api.read_datafeed.side_effect = [ApiException(status=400), ApiException(status=500)]

    with pytest.raises(ApiException) as exception:
        await datafeed_loop.start()
        assert exception.value.status == 500

    datafeed_loop.recreate_datafeed.assert_called_once()
    assert datafeed_api.read_datafeed.call_count == 2


@pytest.mark.asyncio
async def test_400_should_call_recreate_df_return_and_retry(datafeed_loop, datafeed_api, message_sent_event):
    async def read_df(**kwargs):
        if read_df.first_time:
            read_df.first_time = False
            raise ApiException(status=400, reason="")
        await asyncio.sleep(SLEEP_SECONDS)  # to force the switching of tasks
        return message_sent_event

    read_df.first_time = True

    datafeed_api.read_datafeed.side_effect = read_df
    datafeed_loop._retry_config = minimal_retry_config_with_attempts(2)
    datafeed_loop.prepare_datafeed = AsyncMock()
    datafeed_loop.recreate_datafeed = AsyncMock()

    await datafeed_loop.start()

    datafeed_loop.recreate_datafeed.assert_called_once()
    assert datafeed_api.read_datafeed.call_count >= 2


@pytest.mark.asyncio
async def test_unexpected_error_should_be_propagated_and_call_stop_tasks(datafeed_loop, datafeed_api):
    exception = ValueError("An error")
    datafeed_api.read_datafeed.side_effect = exception

    datafeed_loop._prepare_datafeed = AsyncMock()
    datafeed_loop.recreate_datafeed = AsyncMock()
    datafeed_loop._stop_listener_tasks = AsyncMock()

    with pytest.raises(ValueError) as raised_exception:
        await datafeed_loop.start()
        assert raised_exception == exception

    datafeed_loop._prepare_datafeed.assert_called_once()
    datafeed_api.read_datafeed.assert_called_once()
    datafeed_loop.recreate_datafeed.assert_not_called()
    datafeed_loop._stop_listener_tasks.assert_called_once()
