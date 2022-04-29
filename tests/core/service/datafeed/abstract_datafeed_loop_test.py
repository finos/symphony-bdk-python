import asyncio
from unittest.mock import AsyncMock, patch, call

import pytest

from tests.core.service.datafeed.test_fixtures import fixture_initiator_userid, fixture_session_service, \
    fixture_message_sent_v4_event

from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import AbstractDatafeedLoop, RealTimeEvent
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.gen.agent_model.v4_connection_accepted import V4ConnectionAccepted
from symphony.bdk.gen.agent_model.v4_connection_requested import V4ConnectionRequested
from symphony.bdk.gen.agent_model.v4_event import V4Event
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_instant_message_created import V4InstantMessageCreated
from symphony.bdk.gen.agent_model.v4_message import V4Message
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_message_suppressed import V4MessageSuppressed
from symphony.bdk.gen.agent_model.v4_payload import V4Payload
from symphony.bdk.gen.agent_model.v4_room_created import V4RoomCreated
from symphony.bdk.gen.agent_model.v4_room_deactivated import V4RoomDeactivated
from symphony.bdk.gen.agent_model.v4_room_member_demoted_from_owner import V4RoomMemberDemotedFromOwner
from symphony.bdk.gen.agent_model.v4_room_member_promoted_to_owner import V4RoomMemberPromotedToOwner
from symphony.bdk.gen.agent_model.v4_room_reactivated import V4RoomReactivated
from symphony.bdk.gen.agent_model.v4_room_updated import V4RoomUpdated
from symphony.bdk.gen.agent_model.v4_shared_post import V4SharedPost
from symphony.bdk.gen.agent_model.v4_symphony_elements_action import V4SymphonyElementsAction
from symphony.bdk.gen.agent_model.v4_user import V4User
from symphony.bdk.gen.agent_model.v4_user_joined_room import V4UserJoinedRoom
from symphony.bdk.gen.agent_model.v4_user_left_room import V4UserLeftRoom
from symphony.bdk.gen.agent_model.v4_user_requested_to_join_room import V4UserRequestedToJoinRoom
from symphony.bdk.gen.pod_model.user_v2 import UserV2

BOT_USER_ID = 12345
BOT_INFO = UserV2(id=BOT_USER_ID)


async def create_and_await_tasks(datafeed_loop, events):
    tasks = await datafeed_loop._create_listener_tasks(events)
    await asyncio.gather(*tasks)


@pytest.fixture(name="bot_message_sent_event")
def fixture_bot_message_sent_event():
    initiator = V4Initiator(user=V4User(user_id=BOT_USER_ID))
    payload = V4Payload(message_sent=V4MessageSent(message=V4Message(message="message")))
    return V4Event(type=RealTimeEvent.MESSAGESENT.name, payload=payload, initiator=initiator)


@pytest.fixture(name="listener")
def fixture_listener():
    return AsyncMock(wraps=RealTimeEventListener())


@pytest.fixture(name="run_iteration_side_effect")
def fixture_run_iteration_side_effect():
    async def run_iteration(**kwargs):
        await asyncio.sleep(0.001)  # to force the switching of tasks

    return run_iteration


@pytest.fixture(name="bare_df_loop")
def fixture_bare_df_loop(session_service):
    # patch.multiple called in order to be able to instantiate AbstractDatafeedLoop
    with patch.multiple(AbstractDatafeedLoop, __abstractmethods__=set()):
        mock_df = AbstractDatafeedLoop(DatafeedApi(AsyncMock()), session_service, None, BdkConfig())
        mock_df._stop_listener_tasks = AsyncMock()
        mock_df._prepare_datafeed = AsyncMock()
        mock_df._run_loop_iteration = AsyncMock()

        return mock_df


@pytest.fixture(name="df_loop")
def fixture_df_loop(bare_df_loop, listener):
    bare_df_loop._bot_info = BOT_INFO
    bare_df_loop.subscribe(listener)

    return bare_df_loop


@pytest.mark.asyncio
async def test_remove_listener(bare_df_loop):
    listener = RealTimeEventListener()

    assert len(bare_df_loop._listeners) == 0

    bare_df_loop.subscribe(listener)
    assert len(bare_df_loop._listeners) == 1

    bare_df_loop.unsubscribe(listener)
    assert len(bare_df_loop._listeners) == 0


@pytest.mark.asyncio
async def test_start(bare_df_loop, session_service, run_iteration_side_effect):
    bare_df_loop._run_loop_iteration.side_effect = run_iteration_side_effect

    t = asyncio.create_task(bare_df_loop.start())
    await asyncio.sleep(0.001)
    await bare_df_loop.stop()
    await t

    session_service.get_session.assert_called_once()
    assert bare_df_loop._bot_info == BOT_INFO
    bare_df_loop._prepare_datafeed.assert_called_once()
    assert bare_df_loop._run_loop_iteration.call_count >= 1
    bare_df_loop._stop_listener_tasks.assert_called_once()


@pytest.mark.asyncio
async def test_error_in_prepare_should_be_propagated(bare_df_loop):
    exception = ValueError("error")

    bare_df_loop._prepare_datafeed.side_effect = exception

    with pytest.raises(ValueError) as raised_exception:
        await bare_df_loop.start()
        assert raised_exception == exception

    bare_df_loop._prepare_datafeed.assert_called_once()
    bare_df_loop._run_loop_iteration.assert_not_called()
    bare_df_loop._stop_listener_tasks.assert_not_called()


@pytest.mark.asyncio
async def test_unexpected_error_should_be_propagated_and_call_stop_tasks(bare_df_loop):
    exception = ValueError("An error")
    bare_df_loop._run_loop_iteration.side_effect = exception

    with pytest.raises(ValueError) as raised_exception:
        await bare_df_loop.start()
        assert raised_exception == exception

    bare_df_loop._prepare_datafeed.assert_called_once()
    bare_df_loop._run_loop_iteration.assert_called()
    bare_df_loop._stop_listener_tasks.assert_called_once()


@pytest.mark.asyncio
async def test_create_listener_tasks_none(df_loop, listener):
    tasks = await df_loop._create_listener_tasks(None)

    assert len(tasks) == 0
    listener.is_accepting_event.assert_not_called()


@pytest.mark.asyncio
async def test_create_listener_tasks_empty_list(df_loop, listener):
    tasks = await df_loop._create_listener_tasks([])

    assert len(tasks) == 0
    listener.is_accepting_event.assert_not_called()


@pytest.mark.asyncio
async def test_create_listener_tasks_list_with_none(df_loop, listener):
    tasks = await df_loop._create_listener_tasks([None])

    assert len(tasks) == 0
    listener.is_accepting_event.assert_not_called()


@pytest.mark.asyncio
async def test_create_listener_tasks_list_with_element(df_loop, listener, message_sent_v4_event):
    tasks = await df_loop._create_listener_tasks([message_sent_v4_event])

    assert len(tasks) == 1
    listener.is_accepting_event.assert_called_once_with(message_sent_v4_event, BOT_INFO)


@pytest.mark.asyncio
async def test_create_listener_tasks_list_with_element_and_none(df_loop, listener, message_sent_v4_event):
    tasks = await df_loop._create_listener_tasks([message_sent_v4_event, None])

    assert len(tasks) == 1
    listener.is_accepting_event.assert_called_once_with(message_sent_v4_event, BOT_INFO)


@pytest.mark.asyncio
async def test_create_listener_tasks_list_with_two_elements(df_loop, listener, message_sent_v4_event):
    tasks = await df_loop._create_listener_tasks([message_sent_v4_event, message_sent_v4_event])

    assert len(tasks) == 2

    listener.is_accepting_event.assert_has_awaits(
        [call(message_sent_v4_event, BOT_INFO), call(message_sent_v4_event, BOT_INFO)])


@pytest.mark.asyncio
async def test_create_listener_tasks_list_not_accepting_events(df_loop, listener, bot_message_sent_event):
    tasks = await df_loop._create_listener_tasks([bot_message_sent_event])

    assert len(tasks) == 0
    listener.is_accepting_event.assert_called_once_with(bot_message_sent_event, BOT_INFO)


@pytest.mark.asyncio
async def test_create_listener_tasks_list(df_loop, listener, message_sent_v4_event, bot_message_sent_event):
    tasks = await df_loop._create_listener_tasks([message_sent_v4_event, bot_message_sent_event])

    assert len(tasks) == 1
    listener.is_accepting_event.assert_has_awaits(
        [call(message_sent_v4_event, BOT_INFO), call(bot_message_sent_event, BOT_INFO)])


@pytest.mark.asyncio
async def test_create_listener_tasks_list_several_listeners(df_loop, message_sent_v4_event, bot_message_sent_event):
    df_loop.subscribe(RealTimeEventListener())

    tasks = await df_loop._create_listener_tasks([message_sent_v4_event, bot_message_sent_event])

    assert len(tasks) == 2


@pytest.mark.asyncio
async def test_handle_message_sent(df_loop, listener, initiator_userid):
    payload = V4Payload(message_sent=V4MessageSent())
    event = V4Event(type=RealTimeEvent.MESSAGESENT.name, payload=payload, initiator=initiator_userid)

    tasks = await df_loop._create_listener_tasks([event])
    await asyncio.gather(*tasks)

    listener.on_message_sent.assert_called_once_with(initiator_userid, payload.message_sent)


@pytest.mark.asyncio
async def test_handle_shared_post(df_loop, listener, initiator_userid):
    payload = V4Payload(shared_post=V4SharedPost())
    event = V4Event(type=RealTimeEvent.SHAREDPOST.name, payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.on_shared_post.assert_called_once_with(initiator_userid, payload.shared_post)


@pytest.mark.asyncio
async def test_handle_instant_message_created(df_loop, listener, initiator_userid):
    payload = V4Payload(instant_message_created=V4InstantMessageCreated())
    event = V4Event(type=RealTimeEvent.INSTANTMESSAGECREATED.name, payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.on_instant_message_created.assert_called_with(initiator_userid, payload.instant_message_created)


@pytest.mark.asyncio
async def test_handle_room_created(df_loop, listener, initiator_userid):
    payload = V4Payload(room_created=V4RoomCreated())
    event = V4Event(type=RealTimeEvent.ROOMCREATED.name, payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.on_room_created.assert_called_with(initiator_userid, payload.room_created)


@pytest.mark.asyncio
async def test_handle_room_updated(df_loop, listener, initiator_userid):
    payload = V4Payload(room_updated=V4RoomUpdated())
    event = V4Event(type=RealTimeEvent.ROOMUPDATED.name, payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.on_room_updated.assert_called_with(initiator_userid, payload.room_updated)


@pytest.mark.asyncio
async def test_handle_room_deactivated(df_loop, listener, initiator_userid):
    payload = V4Payload(room_deactivated=V4RoomDeactivated())
    event = V4Event(type=RealTimeEvent.ROOMDEACTIVATED.name, payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.on_room_deactivated.assert_called_with(initiator_userid, payload.room_deactivated)


@pytest.mark.asyncio
async def test_handle_room_reactivated(df_loop, listener, initiator_userid):
    payload = V4Payload(room_reactivated=V4RoomReactivated())
    event = V4Event(type=RealTimeEvent.ROOMREACTIVATED.name, payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_INFO)
    listener.on_room_reactivated.assert_called_with(initiator_userid, payload.room_reactivated)


@pytest.mark.asyncio
async def test_handle_user_requested_to_join_room(df_loop, listener, initiator_userid):
    payload = V4Payload(user_requested_to_join_room=V4UserRequestedToJoinRoom())
    event = V4Event(type=RealTimeEvent.USERREQUESTEDTOJOINROOM.name, payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.on_user_requested_to_join_room.assert_called_with(initiator_userid, payload.user_requested_to_join_room)


@pytest.mark.asyncio
async def test_handle_user_joined_room(df_loop, listener, initiator_userid):
    payload = V4Payload(user_joined_room=V4UserJoinedRoom())
    event = V4Event(type=RealTimeEvent.USERJOINEDROOM.name, payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.on_user_joined_room.assert_called_with(initiator_userid, payload.user_joined_room)


@pytest.mark.asyncio
async def test_handle_user_left_room(df_loop, listener, initiator_userid):
    payload = V4Payload(user_left_room=V4UserLeftRoom())
    event = V4Event(type=RealTimeEvent.USERLEFTROOM.name, payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.on_user_left_room.assert_called_with(initiator_userid, payload.user_left_room)


@pytest.mark.asyncio
async def test_handle_room_member_promoted_to_owner(df_loop, listener, initiator_userid):
    payload = V4Payload(room_member_promoted_to_owner=V4RoomMemberPromotedToOwner())
    event = V4Event(type=RealTimeEvent.ROOMMEMBERPROMOTEDTOOWNER.name, payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.on_room_member_promoted_to_owner.assert_called_with(initiator_userid, payload.room_member_promoted_to_owner)


@pytest.mark.asyncio
async def test_handle_room_member_demoted_from_owner(df_loop, listener, initiator_userid):
    payload = V4Payload(room_member_demoted_from_owner=V4RoomMemberDemotedFromOwner())
    event = V4Event(type=RealTimeEvent.ROOMMEMBERDEMOTEDFROMOWNER.name, payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.on_room_demoted_from_owner.assert_called_with(initiator_userid, payload.room_member_demoted_from_owner)


@pytest.mark.asyncio
async def test_handle_connection_requested(df_loop, listener, initiator_userid):
    payload = V4Payload(connection_requested=V4ConnectionRequested())
    event = V4Event(type=RealTimeEvent.CONNECTIONREQUESTED.name, payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.on_connection_requested.assert_called_with(initiator_userid, payload.connection_requested)


@pytest.mark.asyncio
async def test_handle_connection_accepted(df_loop, listener, initiator_userid):
    payload = V4Payload(connection_accepted=V4ConnectionAccepted())
    event = V4Event(type=RealTimeEvent.CONNECTIONACCEPTED.name, payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.on_connection_accepted.assert_called_with(initiator_userid, payload.connection_accepted)


@pytest.mark.asyncio
async def test_handle_message_suppressed(df_loop, listener, initiator_userid):
    payload = V4Payload(message_suppressed=V4MessageSuppressed())
    event = V4Event(type=RealTimeEvent.MESSAGESUPPRESSED.name, payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.on_message_suppressed.assert_called_with(initiator_userid, payload.message_suppressed)


@pytest.mark.asyncio
async def test_handle_symphony_element(df_loop, listener, initiator_userid):
    payload = V4Payload(symphony_elements_action=V4SymphonyElementsAction())
    event = V4Event(type=RealTimeEvent.SYMPHONYELEMENTSACTION.name, payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.on_symphony_elements_action.assert_called_once_with(initiator_userid, payload.symphony_elements_action)


@pytest.mark.asyncio
async def test_handle_unknown_type(df_loop, listener, initiator_userid):
    payload = V4Payload(symphony_elements_action=V4SymphonyElementsAction())
    event = V4Event(type="unknown", payload=payload, initiator=initiator_userid)

    await create_and_await_tasks(df_loop, [event])

    listener.assert_not_awaited()
