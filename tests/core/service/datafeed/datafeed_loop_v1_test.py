from unittest.mock import MagicMock, AsyncMock

import pytest

from symphony.bdk.gen.agent_model.v4_connection_accepted import V4ConnectionAccepted
from symphony.bdk.gen.agent_model.v4_connection_requested import V4ConnectionRequested
from symphony.bdk.gen.agent_model.v4_instant_message_created import V4InstantMessageCreated
from symphony.bdk.gen.agent_model.v4_message_suppressed import V4MessageSuppressed
from symphony.bdk.gen.agent_model.v4_room_created import V4RoomCreated
from symphony.bdk.gen.agent_model.v4_room_deactivated import V4RoomDeactivated
from symphony.bdk.gen.agent_model.v4_room_member_demoted_from_owner import V4RoomMemberDemotedFromOwner
from symphony.bdk.gen.agent_model.v4_room_member_promoted_to_owner import V4RoomMemberPromotedToOwner
from symphony.bdk.gen.agent_model.v4_room_reactivated import V4RoomReactivated
from symphony.bdk.gen.agent_model.v4_room_updated import V4RoomUpdated
from symphony.bdk.gen.agent_model.v4_shared_post import V4SharedPost
from symphony.bdk.gen.agent_model.v4_symphony_elements_action import V4SymphonyElementsAction
from symphony.bdk.gen.agent_model.v4_user_joined_room import V4UserJoinedRoom
from symphony.bdk.gen.agent_model.v4_user_left_room import V4UserLeftRoom
from symphony.bdk.gen.agent_model.v4_user_requested_to_join_room import V4UserRequestedToJoinRoom
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_event import V4Event
from symphony.bdk.gen.agent_model.datafeed import Datafeed
from symphony.bdk.gen.agent_model.v4_payload import V4Payload
from symphony.bdk.gen.agent_model.v4_user import V4User
from symphony.bdk.gen.exceptions import ApiException

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.config.model.bdk_datafeed_config import BdkDatafeedConfig
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import RealTimeEvent
from symphony.bdk.core.service.datafeed.datafeed_loop_v1 import DatafeedLoopV1

from symphony.bdk.gen.api_client import ApiClient
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi

from tests.utils.resource_utils import get_resource_content
from tests.core.test.in_memory_datafeed_id_repository import InMemoryDatafeedIdRepository
from tests.utils.resource_utils import get_config_resource_filepath

DEFAULT_AGENT_BASE_PATH: str = 'https://agent:8443/context'


@pytest.fixture(name='auth_session')
def fixture_auth_session():
    auth_session = AuthSession(None)
    auth_session.session_token = 'session_token'
    auth_session.key_manager_token = 'km_token'
    return auth_session


@pytest.fixture(name='config')
def fixture_config():
    return BdkConfigLoader.load_from_file(get_config_resource_filepath('config.yaml'))


@pytest.fixture(name='datafeed_repository')
def fixture_datafeed_repository():
    return InMemoryDatafeedIdRepository(DEFAULT_AGENT_BASE_PATH)


@pytest.fixture(name='datafeed_api')
def fixture_datafeed_api():
    datafeed_api = MagicMock(DatafeedApi)
    datafeed_api.api_client = MagicMock(ApiClient)
    datafeed_api.v4_datafeed_create_post = AsyncMock()
    datafeed_api.v4_datafeed_id_read_get = AsyncMock()
    return datafeed_api


@pytest.fixture(name='mock_listener')
def fixture_mock_listener():
    return AsyncMock(wraps=RealTimeEventListener())


@pytest.fixture(name='initiator')
def fixture_initiator():
    return V4Initiator(user=V4User(username='username'))


@pytest.fixture(name='message_sent_event')
def fixture_message_sent_event(initiator):
    class EventsMock:
        def __init__(self, individual_event):
            self.value = [individual_event]

    v4_event = V4Event(type=RealTimeEvent.MESSAGESENT.name,
                       payload=V4Payload(message_sent=V4MessageSent()),
                       initiator=initiator)
    event = EventsMock(v4_event)
    return event


@pytest.fixture(name='datafeed_loop_v1')
def fixture_datafeed_loop_v1(datafeed_api, auth_session, config, datafeed_repository):
    return auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config, datafeed_repository)


def auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config, repository=None):
    datafeed_loop = DatafeedLoopV1(datafeed_api, auth_session, config, repository=repository)

    class RealTimeEventListenerImpl(RealTimeEventListener):

        async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
            await datafeed_loop.stop()

    datafeed_loop.subscribe(RealTimeEventListenerImpl())
    return datafeed_loop


@pytest.fixture(name='datafeed_loop_with_listener')
def fixture_datafeed_loop_with_listener(datafeed_api, auth_session, config, mock_listener):
    datafeed_loop = DatafeedLoopV1(datafeed_api, auth_session, config)
    datafeed_loop.subscribe(mock_listener)
    return datafeed_loop


@pytest.mark.asyncio
async def test_start(datafeed_loop_v1, datafeed_api, message_sent_event):
    datafeed_api.v4_datafeed_create_post.return_value = Datafeed(id='test_id')
    datafeed_api.v4_datafeed_id_read_get.return_value = message_sent_event

    await datafeed_loop_v1.start()

    datafeed_api.v4_datafeed_create_post.assert_called_once()
    datafeed_api.v4_datafeed_id_read_get.assert_called_once()

    assert datafeed_loop_v1.datafeed_id == 'test_id'
    assert datafeed_loop_v1.datafeed_repository.read()


@pytest.mark.asyncio
async def test_datafeed_is_reused(datafeed_repository, datafeed_api, auth_session, config, message_sent_event):
    datafeed_repository.write('persisted_id')
    datafeed_loop = auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config, datafeed_repository)

    datafeed_api.v4_datafeed_id_read_get.return_value = message_sent_event

    await datafeed_loop.start()

    datafeed_api.v4_datafeed_create_post.assert_not_called()
    datafeed_api.v4_datafeed_id_read_get.assert_called_once_with(id='persisted_id',
                                                                 session_token='session_token',
                                                                 key_manager_token='km_token')


@pytest.mark.asyncio
async def test_start_recreate_datafeed_error(datafeed_repository, datafeed_api, auth_session, config):
    datafeed_repository.write('persisted_id')
    datafeed_loop = auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config, datafeed_repository)

    datafeed_api.v4_datafeed_id_read_get.side_effect = ApiException(400, 'Expired Datafeed id')
    datafeed_api.v4_datafeed_create_post.side_effect = ApiException(500, 'Unhandled exception')

    with pytest.raises(ApiException):
        await datafeed_loop.start()

    datafeed_api.v4_datafeed_id_read_get.assert_called_once_with(id='persisted_id',
                                                                 session_token='session_token',
                                                                 key_manager_token='km_token')

    datafeed_api.v4_datafeed_create_post.assert_called_once_with(session_token='session_token',
                                                                 key_manager_token='km_token')


@pytest.mark.asyncio
async def test_retrieve_datafeed_from_datafeed_file(tmpdir, datafeed_api, auth_session, config, message_sent_event):
    datafeed_file_content = get_resource_content('datafeed/datafeedId')
    datafeed_file_path = tmpdir.join('datafeed.id')
    datafeed_file_path.write(datafeed_file_content)

    datafeed_config = BdkDatafeedConfig({'idFilePath': str(datafeed_file_path)})
    config.datafeed = datafeed_config

    datafeed_loop = auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config)
    datafeed_api.v4_datafeed_id_read_get.return_value = message_sent_event
    await datafeed_loop.start()

    assert datafeed_loop.datafeed_id == '8e7c8672-220'


@pytest.mark.asyncio
async def test_retrieve_datafeed_from_invalid_datafeed_dir(tmpdir, datafeed_api, auth_session, config,
                                                           message_sent_event):
    datafeed_id_file_content = get_resource_content('datafeed/datafeedId')
    datafeed_id_file_path = tmpdir.join('datafeed.id')
    datafeed_id_file_path.write(datafeed_id_file_content)

    datafeed_config = BdkDatafeedConfig({'idFilePath': str(tmpdir)})
    config.datafeed = datafeed_config

    datafeed_loop = auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config)
    datafeed_api.v4_datafeed_id_read_get.return_value = message_sent_event
    await datafeed_loop.start()

    assert datafeed_loop.datafeed_id == '8e7c8672-220'


@pytest.mark.asyncio
async def test_retrieve_datafeed_id_from_unknown_path(datafeed_api, auth_session, config):
    datafeed_config = BdkDatafeedConfig({'idFilePath': 'unknown_path'})
    config.datafeed = datafeed_config

    datafeed_loop = auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config)

    assert datafeed_loop.datafeed_id is None


@pytest.mark.asyncio
async def test_retrieve_datafeed_id_from_empty_file(tmpdir, datafeed_api, auth_session, config):
    datafeed_file_path = tmpdir.join('datafeed.id')

    datafeed_config = BdkDatafeedConfig({'idFilePath': str(datafeed_file_path)})
    config.datafeed = datafeed_config

    datafeed_loop = auto_stopping_datafeed_loop_v1(datafeed_api, auth_session, config)

    assert datafeed_loop.datafeed_id is None


@pytest.mark.asyncio
async def test_handle_message_sent(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(message_sent=V4MessageSent())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.MESSAGESENT.name, payload=payload, initiator=initiator)])

    mock_listener.on_message_sent.assert_called_once_with(initiator, payload.message_sent)


@pytest.mark.asyncio
async def test_handle_shared_post(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(shared_post=V4SharedPost())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.SHAREDPOST.name, payload=payload, initiator=initiator)])

    mock_listener.on_shared_post.assert_called_once_with(initiator, payload.shared_post)


@pytest.mark.asyncio
async def test_handle_instant_message_created(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(instant_message_created=V4InstantMessageCreated())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.INSTANTMESSAGECREATED.name, payload=payload, initiator=initiator)])

    mock_listener.on_instant_message_created.assert_called_once_with(initiator, payload.instant_message_created)


@pytest.mark.asyncio
async def test_handle_room_created(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(room_created=V4RoomCreated())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.ROOMCREATED.name, payload=payload, initiator=initiator)])

    mock_listener.on_room_created.assert_called_once_with(initiator, payload.room_created)


@pytest.mark.asyncio
async def test_handle_room_updated(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(room_updated=V4RoomUpdated())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.ROOMUPDATED.name, payload=payload, initiator=initiator)])

    mock_listener.on_room_updated.assert_called_once_with(initiator, payload.room_updated)


@pytest.mark.asyncio
async def test_handle_room_deactivated(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(room_deactivated=V4RoomDeactivated())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.ROOMDEACTIVATED.name, payload=payload, initiator=initiator)])

    mock_listener.on_room_deactivated.assert_called_once_with(initiator, payload.room_deactivated)


@pytest.mark.asyncio
async def test_handle_room_reactivated(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(room_reactivated=V4RoomReactivated())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.ROOMREACTIVATED.name, payload=payload, initiator=initiator)])

    mock_listener.on_room_reactivated.assert_called_once_with(initiator, payload.room_reactivated)


@pytest.mark.asyncio
async def test_handle_user_requested_to_join_room(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(user_requested_to_join_room=V4UserRequestedToJoinRoom())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.USERREQUESTEDTOJOINROOM.name, payload=payload, initiator=initiator)])

    mock_listener.on_user_requested_to_join_room.assert_called_once_with(initiator, payload.user_requested_to_join_room)


@pytest.mark.asyncio
async def test_handle_user_joined_room(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(user_joined_room=V4UserJoinedRoom())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.USERJOINEDROOM.name, payload=payload, initiator=initiator)])

    mock_listener.on_user_joined_room.assert_called_once_with(initiator, payload.user_joined_room)


@pytest.mark.asyncio
async def test_handle_user_left_room(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(user_left_room=V4UserLeftRoom())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.USERLEFTROOM.name, payload=payload, initiator=initiator)])

    mock_listener.on_user_left_room.assert_called_once_with(initiator, payload.user_left_room)


@pytest.mark.asyncio
async def test_handle_room_member_promoted_to_owner(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(room_member_promoted_to_owner=V4RoomMemberPromotedToOwner())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.ROOMMEMBERPROMOTEDTOOWNER.name, payload=payload, initiator=initiator)])

    mock_listener.on_room_member_promoted_to_owner.assert_called_once_with(initiator,
                                                                           payload.room_member_promoted_to_owner)


@pytest.mark.asyncio
async def test_handle_room_member_demoted_from_owner(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(room_member_demoted_from_owner=V4RoomMemberDemotedFromOwner())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.ROOMMEMBERDEMOTEDFROMOWNER.name, payload=payload, initiator=initiator)])

    mock_listener.on_room_demoted_from_owner.assert_called_once_with(initiator, payload.room_member_demoted_from_owner)


@pytest.mark.asyncio
async def test_handle_connection_requested(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(connection_requested=V4ConnectionRequested())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.CONNECTIONREQUESTED.name, payload=payload, initiator=initiator)])

    mock_listener.on_connection_requested.assert_called_once_with(initiator, payload.connection_requested)


@pytest.mark.asyncio
async def test_handle_connection_accepted(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(connection_accepted=V4ConnectionAccepted())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.CONNECTIONACCEPTED.name, payload=payload, initiator=initiator)])

    mock_listener.on_connection_accepted.assert_called_once_with(initiator, payload.connection_accepted)


@pytest.mark.asyncio
async def test_handle_message_suppressed(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(message_suppressed=V4MessageSuppressed())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.MESSAGESUPPRESSED.name, payload=payload, initiator=initiator)])

    mock_listener.on_message_suppressed.assert_called_once_with(initiator, payload.message_suppressed)


@pytest.mark.asyncio
async def test_handle_symphony_element(datafeed_loop_with_listener, mock_listener, initiator):
    payload = V4Payload(symphony_elements_action=V4SymphonyElementsAction())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.SYMPHONYELEMENTSACTION.name, payload=payload, initiator=initiator)])

    mock_listener.on_symphony_elements_action.assert_called_once_with(initiator, payload.symphony_elements_action)


@pytest.mark.asyncio
async def test_handle_bot_event(datafeed_loop_with_listener, mock_listener, config):
    initiator = V4Initiator(user=V4User(username=config.bot.username))
    payload = V4Payload(message_sent=V4MessageSent())

    await datafeed_loop_with_listener.handle_v4_event_list(
        [V4Event(type=RealTimeEvent.MESSAGESENT.name, payload=payload, initiator=initiator)])

    mock_listener.assert_not_called()


@pytest.mark.asyncio
async def test_handle_empty_event_list(datafeed_loop_with_listener, mock_listener):
    await datafeed_loop_with_listener.handle_v4_event_list([])

    mock_listener.assert_not_called()


@pytest.mark.asyncio
async def test_handle_event_list_with_none(datafeed_loop_with_listener, mock_listener):
    await datafeed_loop_with_listener.handle_v4_event_list([None])

    mock_listener.assert_not_called()


@pytest.mark.asyncio
async def test_handle_event_with_unknown_event_type(datafeed_loop_with_listener, mock_listener):
    await datafeed_loop_with_listener.handle_v4_event_list([V4Event(type='unknown type')])

    mock_listener.assert_not_called()
