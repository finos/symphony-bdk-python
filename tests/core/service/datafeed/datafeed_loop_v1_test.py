# ruff: noqa
import asyncio
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from tests.core.service.datafeed.test_fixtures import (
    fixture_initiator_username,
    fixture_session_service,
    fixture_auth_session,
)

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.config.model.bdk_datafeed_config import BdkDatafeedConfig
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import RealTimeEvent
from symphony.bdk.core.service.datafeed.datafeed_loop_v1 import DatafeedLoopV1
from symphony.bdk.core.service.datafeed.exception import EventError
from symphony.bdk.core.service.datafeed.real_time_event_listener import (
    RealTimeEventListener,
)
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.gen.agent_model.datafeed import Datafeed
from symphony.bdk.gen.agent_model.v4_event import V4Event
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_payload import V4Payload
from symphony.bdk.gen.api_client import ApiClient
from symphony.bdk.gen.exceptions import ApiException
from tests.core.config import minimal_retry_config_with_attempts
from tests.core.test.in_memory_datafeed_id_repository import (
    InMemoryDatafeedIdRepository,
)
from tests.utils.resource_utils import (
    get_config_resource_filepath,
    get_resource_content,
)

SLEEP_SECONDS = 0.0001


class EventsMock:
    def __init__(self, events):
        self.value = events


@pytest.fixture(name="config")
def fixture_config():
    return BdkConfigLoader.load_from_file(get_config_resource_filepath("config.yaml"))


@pytest.fixture(name="datafeed_repository")
def fixture_datafeed_repository():
    return InMemoryDatafeedIdRepository("https://agent:8443/context")


@pytest.fixture(name="datafeed_api")
def fixture_datafeed_api():
    datafeed_api = MagicMock(DatafeedApi)
    datafeed_api.api_client = MagicMock(ApiClient)
    datafeed_api.v4_datafeed_create_post = AsyncMock()
    datafeed_api.v4_datafeed_id_read_get = AsyncMock()
    return datafeed_api


@pytest.fixture(name="message_sent")
def fixture_message_sent(initiator_username):
    return V4Event(
        type=RealTimeEvent.MESSAGESENT.name,
        payload=V4Payload(message_sent=V4MessageSent()),
        initiator=initiator_username,
    )


@pytest.fixture(name="message_sent_event")
def fixture_message_sent_event(message_sent):
    return EventsMock([message_sent])


@pytest.fixture(name="read_df_side_effect")
def fixture_read_df_side_effect(message_sent_event):
    async def read_df(**kwargs):
        await asyncio.sleep(SLEEP_SECONDS)  # to force the switching of tasks
        return message_sent_event

    return read_df


@pytest.fixture(name="read_df_loop_side_effect")
def fixture_read_df_loop_side_effect(message_sent):
    async def read_df(**kwargs):
        await asyncio.sleep(SLEEP_SECONDS)  # to force the switching of tasks
        return [message_sent]

    return read_df


@pytest.fixture(name="datafeed_loop_v1")
def fixture_datafeed_loop_v1(
    datafeed_api, session_service, auth_session, config, datafeed_repository
):
    df_loop = auto_stopping_datafeed_loop_v1(
        datafeed_api, session_service, auth_session, config, datafeed_repository
    )
    df_loop._retry_config = minimal_retry_config_with_attempts(1)
    return df_loop


@pytest.fixture(name="mock_datafeed_loop_v1")
def fixture_mock_datafeed_loop_v1_(
    datafeed_api, session_service, config, datafeed_repository, read_df_loop_side_effect
):
    datafeed_loop = DatafeedLoopV1(
        datafeed_api, session_service, None, config, repository=datafeed_repository
    )
    datafeed_loop._prepare_datafeed = AsyncMock()
    datafeed_loop.recreate_datafeed = AsyncMock()
    datafeed_loop._read_datafeed = AsyncMock(side_effect=read_df_loop_side_effect)

    return datafeed_loop


def auto_stopping_datafeed_loop_v1(
    datafeed_api, session_service, auth_session, config, repository=None
):
    datafeed_loop = DatafeedLoopV1(
        datafeed_api, session_service, auth_session, config, repository
    )

    class RealTimeEventListenerImpl(RealTimeEventListener):
        async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
            await datafeed_loop.stop()

    datafeed_loop.subscribe(RealTimeEventListenerImpl())
    return datafeed_loop


@pytest.mark.asyncio
async def test_start(
    datafeed_loop_v1, datafeed_api, session_service, read_df_side_effect
):
    datafeed_api.v4_datafeed_create_post.return_value = Datafeed(id="test_id")
    datafeed_api.v4_datafeed_id_read_get.side_effect = read_df_side_effect

    await datafeed_loop_v1.start()

    session_service.get_session.assert_called_once()
    datafeed_api.v4_datafeed_create_post.assert_called_once()
    assert datafeed_api.v4_datafeed_id_read_get.call_count >= 1

    assert datafeed_loop_v1._datafeed_id == "test_id"
    assert datafeed_loop_v1._datafeed_repository.read()


@pytest.mark.asyncio
async def test_start_already_started_datafeed_v1_loop_should_throw_error(
    datafeed_loop_v1,
):
    datafeed_loop_v1._running = True
    with pytest.raises(
        RuntimeError, match="The datafeed service V1 is already started"
    ):
        await datafeed_loop_v1.start()


@pytest.mark.asyncio
async def test_read_datafeed_none_list(datafeed_loop_v1, datafeed_api):
    datafeed_api.v4_datafeed_id_read_get.return_value = None

    assert await datafeed_loop_v1._read_datafeed() == []


@pytest.mark.asyncio
async def test_read_datafeed_no_value(datafeed_loop_v1, datafeed_api):
    datafeed_api.v4_datafeed_id_read_get.return_value = EventsMock(None)

    assert await datafeed_loop_v1._read_datafeed() == []


@pytest.mark.asyncio
async def test_read_datafeed_empty_list(datafeed_loop_v1, datafeed_api):
    datafeed_api.v4_datafeed_id_read_get.return_value = EventsMock([])

    assert await datafeed_loop_v1._read_datafeed() == []


@pytest.mark.asyncio
async def test_read_datafeed_non_empty_list(
    datafeed_loop_v1, datafeed_api, message_sent
):
    events = [message_sent]
    datafeed_api.v4_datafeed_id_read_get.return_value = EventsMock(events)

    assert await datafeed_loop_v1._read_datafeed() == events


@pytest.mark.asyncio
async def test_datafeed_is_reused(
    datafeed_repository,
    datafeed_api,
    session_service,
    auth_session,
    config,
    read_df_side_effect,
):
    datafeed_repository.write("persisted_id")
    datafeed_loop = auto_stopping_datafeed_loop_v1(
        datafeed_api, session_service, auth_session, config, datafeed_repository
    )

    datafeed_api.v4_datafeed_id_read_get.side_effect = read_df_side_effect

    await datafeed_loop.start()

    datafeed_api.v4_datafeed_create_post.assert_not_called()
    datafeed_api.v4_datafeed_id_read_get.assert_called_with(
        id="persisted_id", session_token="session_token", key_manager_token="km_token"
    )


@pytest.mark.asyncio
async def test_start_recreate_datafeed_error(
    datafeed_repository, datafeed_api, session_service, auth_session, config
):
    datafeed_repository.write("persisted_id")
    datafeed_loop = auto_stopping_datafeed_loop_v1(
        datafeed_api, session_service, auth_session, config, datafeed_repository
    )

    datafeed_api.v4_datafeed_id_read_get.side_effect = ApiException(
        400, "Expired Datafeed id"
    )
    datafeed_api.v4_datafeed_create_post.side_effect = ApiException(
        400, "Unhandled exception"
    )

    with pytest.raises(ApiException):
        await datafeed_loop.start()

    datafeed_api.v4_datafeed_id_read_get.assert_called_once_with(
        id="persisted_id", session_token="session_token", key_manager_token="km_token"
    )

    datafeed_api.v4_datafeed_create_post.assert_called_once_with(
        session_token="session_token", key_manager_token="km_token"
    )


@pytest.mark.asyncio
async def test_retrieve_datafeed_from_datafeed_file(
    tmpdir, datafeed_api, session_service, auth_session, config, read_df_side_effect
):
    datafeed_file_content = get_resource_content("datafeed/datafeedId")
    datafeed_file_path = tmpdir.join("datafeed.id")
    datafeed_file_path.write(datafeed_file_content)

    datafeed_config = BdkDatafeedConfig({"idFilePath": str(datafeed_file_path)})
    config.datafeed = datafeed_config

    datafeed_loop = auto_stopping_datafeed_loop_v1(
        datafeed_api, session_service, auth_session, config
    )
    datafeed_api.v4_datafeed_id_read_get.side_effect = read_df_side_effect
    await datafeed_loop.start()

    assert datafeed_loop._datafeed_id == "8e7c8672-220"


@pytest.mark.asyncio
async def test_retrieve_datafeed_from_invalid_datafeed_dir(
    tmpdir, datafeed_api, session_service, auth_session, config, read_df_side_effect
):
    datafeed_id_file_content = get_resource_content("datafeed/datafeedId")
    datafeed_id_file_path = tmpdir.join("datafeed.id")
    datafeed_id_file_path.write(datafeed_id_file_content)

    datafeed_config = BdkDatafeedConfig({"idFilePath": str(tmpdir)})
    config.datafeed = datafeed_config

    datafeed_loop = auto_stopping_datafeed_loop_v1(
        datafeed_api, session_service, auth_session, config
    )
    datafeed_api.v4_datafeed_id_read_get.side_effect = read_df_side_effect
    await datafeed_loop.start()

    assert datafeed_loop._datafeed_id == "8e7c8672-220"


@pytest.mark.asyncio
async def test_retrieve_datafeed_id_from_unknown_path(
    datafeed_api, session_service, auth_session, config
):
    datafeed_config = BdkDatafeedConfig({"idFilePath": "unknown_path"})
    config.datafeed = datafeed_config

    datafeed_loop = auto_stopping_datafeed_loop_v1(
        datafeed_api, session_service, auth_session, config
    )

    assert datafeed_loop._datafeed_id is None


@pytest.mark.asyncio
async def test_retrieve_datafeed_id_from_empty_file(
    tmpdir, datafeed_api, session_service, auth_session, config
):
    datafeed_file_path = tmpdir.join("datafeed.id")

    datafeed_config = BdkDatafeedConfig({"idFilePath": str(datafeed_file_path)})
    config.datafeed = datafeed_config

    datafeed_loop = auto_stopping_datafeed_loop_v1(
        datafeed_api, auth_session, session_service, config
    )

    assert datafeed_loop._datafeed_id is None


@pytest.mark.asyncio
async def test_no_listener_task(mock_datafeed_loop_v1):
    class RealTimeEventListenerImpl(RealTimeEventListener):
        async def is_accepting_event(self, event: V4Event, username: str) -> bool:
            return False

    listener = AsyncMock(wraps=RealTimeEventListenerImpl())
    mock_datafeed_loop_v1.subscribe(listener)

    t = asyncio.create_task(mock_datafeed_loop_v1.start())
    await asyncio.sleep(SLEEP_SECONDS)  # to force task switching
    await mock_datafeed_loop_v1.stop()
    await t

    listener.on_message_sent.assert_not_called()


@pytest.mark.asyncio
async def test_listener_called(mock_datafeed_loop_v1, message_sent, initiator_username):
    class RealTimeEventListenerImpl(RealTimeEventListener):
        async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
            await mock_datafeed_loop_v1.stop()

    listener = AsyncMock(wraps=RealTimeEventListenerImpl())
    mock_datafeed_loop_v1.subscribe(listener)

    await mock_datafeed_loop_v1.start()

    listener.on_message_sent.assert_called_once_with(
        initiator_username, message_sent.payload.message_sent
    )


@pytest.mark.asyncio
async def test_exception_in_listener_ignored(
    mock_datafeed_loop_v1, message_sent, initiator_username
):
    class RealTimeEventListenerImpl(RealTimeEventListener):
        count = 0

        async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
            self.count += 1
            if self.count == 1:
                raise ValueError()
            await mock_datafeed_loop_v1.stop()

    listener = AsyncMock(wraps=RealTimeEventListenerImpl())
    mock_datafeed_loop_v1.subscribe(listener)

    await mock_datafeed_loop_v1.start()

    listener_call = call(initiator_username, message_sent.payload.message_sent)
    listener.on_message_sent.assert_has_awaits([listener_call, listener_call])


@pytest.mark.asyncio
async def test_event_error_in_listener_ignored(
    mock_datafeed_loop_v1, message_sent, initiator_username
):
    class RealTimeEventListenerImpl(RealTimeEventListener):
        count = 0

        async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
            self.count += 1
            if self.count == 1:
                raise EventError()
            await mock_datafeed_loop_v1.stop()

    listener = AsyncMock(wraps=RealTimeEventListenerImpl())
    mock_datafeed_loop_v1.subscribe(listener)

    await mock_datafeed_loop_v1.start()

    listener_call = call(initiator_username, message_sent.payload.message_sent)
    listener.on_message_sent.assert_has_awaits([listener_call, listener_call])


@pytest.mark.asyncio
async def test_events_concurrency_within_same_read_df_chunk(
    mock_datafeed_loop_v1, message_sent
):
    class QueueListener(RealTimeEventListener):
        def __init__(self):
            self.queue = asyncio.Queue()
            self.count = 0

        async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
            self.count += 1
            if self.count == 1:
                await self.queue.get()
                await mock_datafeed_loop_v1.stop()
            elif self.count == 2:
                await self.queue.put("message")

    async def read_df(**kwargs):
        await asyncio.sleep(SLEEP_SECONDS)  # to force the switching of tasks
        return [message_sent, message_sent]

    mock_datafeed_loop_v1._read_datafeed.side_effect = read_df
    mock_datafeed_loop_v1.subscribe(QueueListener())

    await mock_datafeed_loop_v1.start()  # test no deadlock


@pytest.mark.asyncio
async def test_error_in_prepare_should_be_propagated(mock_datafeed_loop_v1):
    exception = ValueError("error")

    mock_datafeed_loop_v1._run_loop_iteration = AsyncMock()
    mock_datafeed_loop_v1._stop_listener_tasks = AsyncMock()
    mock_datafeed_loop_v1._prepare_datafeed.side_effect = exception

    with pytest.raises(ValueError) as raised_exception:
        await mock_datafeed_loop_v1.start()
        assert raised_exception == exception

    mock_datafeed_loop_v1._prepare_datafeed.assert_called_once()
    mock_datafeed_loop_v1._run_loop_iteration.assert_not_called()
    mock_datafeed_loop_v1._stop_listener_tasks.assert_not_called()
