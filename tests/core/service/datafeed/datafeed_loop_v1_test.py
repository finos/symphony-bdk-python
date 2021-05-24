import asyncio
from unittest.mock import MagicMock, AsyncMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.config.model.bdk_datafeed_config import BdkDatafeedConfig
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import RealTimeEvent
from symphony.bdk.core.service.datafeed.datafeed_loop_v1 import DatafeedLoopV1
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.gen.agent_model.datafeed import Datafeed
from symphony.bdk.gen.agent_model.v4_event import V4Event
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_payload import V4Payload
from symphony.bdk.gen.agent_model.v4_user import V4User
from symphony.bdk.gen.api_client import ApiClient
from symphony.bdk.gen.exceptions import ApiException
from tests.core.config import minimal_retry_config_with_attempts
from tests.core.test.in_memory_datafeed_id_repository import InMemoryDatafeedIdRepository
from tests.utils.resource_utils import get_config_resource_filepath
from tests.utils.resource_utils import get_resource_content

DEFAULT_AGENT_BASE_PATH: str = "https://agent:8443/context"


class EventsMock:
    def __init__(self, events):
        self.value = events


@pytest.fixture(name="auth_session")
def fixture_auth_session():
    auth_session = AuthSession(None)
    auth_session.session_token = "session_token"
    auth_session.key_manager_token = "km_token"
    return auth_session


@pytest.fixture(name="config")
def fixture_config():
    return BdkConfigLoader.load_from_file(get_config_resource_filepath("config.yaml"))


@pytest.fixture(name="datafeed_repository")
def fixture_datafeed_repository():
    return InMemoryDatafeedIdRepository(DEFAULT_AGENT_BASE_PATH)


@pytest.fixture(name="datafeed_api")
def fixture_datafeed_api():
    datafeed_api = MagicMock(DatafeedApi)
    datafeed_api.api_client = MagicMock(ApiClient)
    datafeed_api.v4_datafeed_create_post = AsyncMock()
    datafeed_api.v4_datafeed_id_read_get = AsyncMock()
    return datafeed_api


@pytest.fixture(name="mock_listener")
def fixture_mock_listener():
    listener = AsyncMock(wraps=RealTimeEventListener())
    listener.is_accepting_event.return_value = True
    return listener


@pytest.fixture(name="message_sent")
def fixture_message_sent():
    initiator = V4Initiator(user=V4User(username="username"))
    return V4Event(type=RealTimeEvent.MESSAGESENT.name,
                   payload=V4Payload(message_sent=V4MessageSent()),
                   initiator=initiator)


@pytest.fixture(name="message_sent_event")
def fixture_message_sent_event(message_sent):
    return EventsMock([message_sent])


@pytest.fixture(name="read_df_side_effect")
def fixture_read_df_side_effect(message_sent_event):
    async def read_df(**kwargs):
        await asyncio.sleep(0.001)  # to force the switching of tasks
        return message_sent_event

    return read_df


@pytest.fixture(name="datafeed_loop_v1")
def fixture_datafeed_loop_v1(datafeed_api, auth_session, config, datafeed_repository):
    df_loop = auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config, datafeed_repository)
    df_loop._retry_config = minimal_retry_config_with_attempts(1)
    return df_loop


def auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config, repository=None):
    datafeed_loop = DatafeedLoopV1(datafeed_api, auth_session, config, repository=repository)

    class RealTimeEventListenerImpl(RealTimeEventListener):

        async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
            await datafeed_loop.stop()

    datafeed_loop.subscribe(RealTimeEventListenerImpl())
    return datafeed_loop


@pytest.fixture(name="datafeed_loop_with_listener")
def fixture_datafeed_loop_with_listener(datafeed_api, auth_session, config, mock_listener):
    datafeed_loop = DatafeedLoopV1(datafeed_api, auth_session, config)
    datafeed_loop.subscribe(mock_listener)
    return datafeed_loop


@pytest.mark.asyncio
async def test_start(datafeed_loop_v1, datafeed_api, read_df_side_effect):
    datafeed_api.v4_datafeed_create_post.return_value = Datafeed(id="test_id")
    datafeed_api.v4_datafeed_id_read_get.side_effect = read_df_side_effect

    await datafeed_loop_v1.start()

    datafeed_api.v4_datafeed_create_post.assert_called_once()
    assert datafeed_api.v4_datafeed_id_read_get.call_count >= 1

    assert datafeed_loop_v1._datafeed_id == "test_id"
    assert datafeed_loop_v1._datafeed_repository.read()


@pytest.mark.asyncio
async def test_read_datafeed_none_list(datafeed_loop_v1, datafeed_api):
    datafeed_api.v4_datafeed_id_read_get.return_value = None

    assert await datafeed_loop_v1.read_datafeed() is None


@pytest.mark.asyncio
async def test_read_datafeed_no_value(datafeed_loop_v1, datafeed_api):
    datafeed_api.v4_datafeed_id_read_get.return_value = EventsMock(None)

    assert await datafeed_loop_v1.read_datafeed() is None


@pytest.mark.asyncio
async def test_read_datafeed_empty_list(datafeed_loop_v1, datafeed_api):
    datafeed_api.v4_datafeed_id_read_get.return_value = EventsMock([])

    assert await datafeed_loop_v1.read_datafeed() is None


@pytest.mark.asyncio
async def test_read_datafeed_non_empty_list(datafeed_loop_v1, datafeed_api, message_sent):
    events = [message_sent]
    datafeed_api.v4_datafeed_id_read_get.return_value = EventsMock(events)

    assert await datafeed_loop_v1.read_datafeed() == events


@pytest.mark.asyncio
async def test_datafeed_is_reused(datafeed_repository, datafeed_api, auth_session, config, read_df_side_effect):
    datafeed_repository.write("persisted_id")
    datafeed_loop = auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config, datafeed_repository)

    datafeed_api.v4_datafeed_id_read_get.side_effect = read_df_side_effect

    await datafeed_loop.start()

    datafeed_api.v4_datafeed_create_post.assert_not_called()
    datafeed_api.v4_datafeed_id_read_get.assert_called_with(id="persisted_id",
                                                            session_token="session_token",
                                                            key_manager_token="km_token")


@pytest.mark.asyncio
async def test_start_recreate_datafeed_error(datafeed_repository, datafeed_api, auth_session, config):
    datafeed_repository.write("persisted_id")
    datafeed_loop = auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config, datafeed_repository)

    datafeed_api.v4_datafeed_id_read_get.side_effect = ApiException(400, "Expired Datafeed id")
    datafeed_api.v4_datafeed_create_post.side_effect = ApiException(400, "Unhandled exception")

    with pytest.raises(ApiException):
        await datafeed_loop.start()

    datafeed_api.v4_datafeed_id_read_get.assert_called_once_with(id="persisted_id",
                                                                 session_token="session_token",
                                                                 key_manager_token="km_token")

    datafeed_api.v4_datafeed_create_post.assert_called_once_with(session_token="session_token",
                                                                 key_manager_token="km_token")


@pytest.mark.asyncio
async def test_retrieve_datafeed_from_datafeed_file(tmpdir, datafeed_api, auth_session, config, read_df_side_effect):
    datafeed_file_content = get_resource_content("datafeed/datafeedId")
    datafeed_file_path = tmpdir.join("datafeed.id")
    datafeed_file_path.write(datafeed_file_content)

    datafeed_config = BdkDatafeedConfig({"idFilePath": str(datafeed_file_path)})
    config.datafeed = datafeed_config

    datafeed_loop = auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config)
    datafeed_api.v4_datafeed_id_read_get.side_effect = read_df_side_effect
    await datafeed_loop.start()

    assert datafeed_loop._datafeed_id == "8e7c8672-220"


@pytest.mark.asyncio
async def test_retrieve_datafeed_from_invalid_datafeed_dir(tmpdir, datafeed_api, auth_session, config,
                                                           read_df_side_effect):
    datafeed_id_file_content = get_resource_content("datafeed/datafeedId")
    datafeed_id_file_path = tmpdir.join("datafeed.id")
    datafeed_id_file_path.write(datafeed_id_file_content)

    datafeed_config = BdkDatafeedConfig({"idFilePath": str(tmpdir)})
    config.datafeed = datafeed_config

    datafeed_loop = auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config)
    datafeed_api.v4_datafeed_id_read_get.side_effect = read_df_side_effect
    await datafeed_loop.start()

    assert datafeed_loop._datafeed_id == "8e7c8672-220"


@pytest.mark.asyncio
async def test_retrieve_datafeed_id_from_unknown_path(datafeed_api, auth_session, config):
    datafeed_config = BdkDatafeedConfig({"idFilePath": "unknown_path"})
    config.datafeed = datafeed_config

    datafeed_loop = auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config)

    assert datafeed_loop._datafeed_id is None


@pytest.mark.asyncio
async def test_retrieve_datafeed_id_from_empty_file(tmpdir, datafeed_api, auth_session, config):
    datafeed_file_path = tmpdir.join("datafeed.id")

    datafeed_config = BdkDatafeedConfig({"idFilePath": str(datafeed_file_path)})
    config.datafeed = datafeed_config

    datafeed_loop = auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config)

    assert datafeed_loop._datafeed_id is None
