import asyncio
from unittest.mock import AsyncMock, patch, Mock

import pytest

from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import AbstractDatafeedLoop, RealTimeEvent
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.gen import ApiException
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

BOT_USER = "bot-user"


class ClosingListener(RealTimeEventListener):
    def __init__(self, df_loop):
        self.df_loop = df_loop

    async def on_message_sent(self, initiator, event):
        await self.df_loop.stop()

    @staticmethod
    async def is_accepting_event(event, username):
        return True


def assert_prepared_read_df_stop_tasks_called(df_loop):
    df_loop.prepare_datafeed.assert_called_once()
    assert df_loop.read_datafeed.call_count >= 1
    df_loop._stop_listener_tasks.assert_called_once()


def assert_is_accepting_event_on_message_sent_called(listener, message_sent_event):
    listener.is_accepting_event.assert_called_with(message_sent_event, BOT_USER)
    listener.on_message_sent.assert_called_once_with(message_sent_event.initiator,
                                                     message_sent_event.payload.message_sent)


async def handle_events_and_wait_for_completion(df_loop, events):
    await df_loop.handle_v4_event_list(events)

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    await asyncio.gather(*tasks)


@pytest.fixture(name="initiator")
def fixture_initiator():
    return V4Initiator(user=V4User(username="username"))


@pytest.fixture(name="message_sent_event")
def fixture_message_sent_event(initiator):
    payload = V4Payload(message_sent=V4MessageSent(message=V4Message(message="message")))
    return V4Event(type=RealTimeEvent.MESSAGESENT.name, payload=payload, initiator=initiator)


@pytest.fixture(name="read_df_side_effect")
def fixture_read_df_side_effect(message_sent_event):
    async def read_df(**kwargs):
        await asyncio.sleep(0.001)  # to force the switching of tasks
        return [message_sent_event]

    return read_df


@pytest.fixture(name="bare_df_loop")
def fixture_bare_df_loop():
    # patch.multiple called in order to be able to instantiate AbstractDatafeedLoop
    with patch.multiple(AbstractDatafeedLoop, __abstractmethods__=set()):
        mock_df = AbstractDatafeedLoop(DatafeedApi(AsyncMock()), None, BdkConfig(bot={"username": BOT_USER}))
        mock_df._stop_listener_tasks = AsyncMock(wraps=mock_df._stop_listener_tasks)
        mock_df.read_datafeed = AsyncMock()
        mock_df.prepare_datafeed = AsyncMock()
        mock_df.recreate_datafeed = AsyncMock()

        return mock_df


@pytest.fixture(name="df_loop")
def fixture_autoclosing_df_loop(bare_df_loop):
    listener = AsyncMock(wraps=ClosingListener(bare_df_loop))
    bare_df_loop.subscribe(listener)

    return bare_df_loop


@pytest.fixture(name="listener")
def fixture_listener(df_loop):
    return df_loop.listeners[0]


@pytest.mark.asyncio
async def test_remove_listener(df_loop, listener):
    assert len(df_loop.listeners) == 1
    df_loop.unsubscribe(listener)
    assert len(df_loop.listeners) == 0


@pytest.mark.asyncio
async def test_start(df_loop, listener, read_df_side_effect, message_sent_event):
    df_loop.read_datafeed.side_effect = read_df_side_effect

    await df_loop.start()

    assert_prepared_read_df_stop_tasks_called(df_loop)
    assert_is_accepting_event_on_message_sent_called(listener, message_sent_event)


@pytest.mark.asyncio
async def test_is_accepting_event_false(df_loop, listener, read_df_side_effect, message_sent_event):
    df_loop.read_datafeed.side_effect = read_df_side_effect

    non_accepting_event_listener = AsyncMock()
    non_accepting_event_listener.is_accepting_event.return_value = False

    df_loop.subscribe(non_accepting_event_listener)
    await df_loop.start()

    assert_prepared_read_df_stop_tasks_called(df_loop)
    assert_is_accepting_event_on_message_sent_called(listener, message_sent_event)

    non_accepting_event_listener.is_accepting_event.assert_called_with(message_sent_event, BOT_USER)
    non_accepting_event_listener.on_message_sent.assert_not_called()


@pytest.mark.asyncio
async def test_error_in_listener(df_loop, listener, read_df_side_effect, message_sent_event):
    df_loop.read_datafeed.side_effect = read_df_side_effect

    error_listener = AsyncMock()
    error_listener.is_accepting_event.return_value = True
    error_listener.on_message_sent.side_effect = ValueError("Error in listener")

    df_loop.subscribe(error_listener)
    await df_loop.start()  # No error raised

    assert_prepared_read_df_stop_tasks_called(df_loop)
    assert_is_accepting_event_on_message_sent_called(listener, message_sent_event)
    assert_is_accepting_event_on_message_sent_called(error_listener, message_sent_event)


@pytest.mark.asyncio
async def test_400_should_call_recreate_df(df_loop, listener, message_sent_event):
    async def read_df(**kwargs):
        if read_df.first_time:
            read_df.first_time = False
            raise ApiException(status=400, reason="")
        await asyncio.sleep(0.001)
        return [message_sent_event]

    read_df.first_time = True

    df_loop.read_datafeed.side_effect = read_df

    await df_loop.start()

    df_loop.prepare_datafeed.assert_called_once()
    assert df_loop.read_datafeed.call_count >= 2
    df_loop.recreate_datafeed.assert_called_once()

    assert_is_accepting_event_on_message_sent_called(listener, message_sent_event)


@pytest.mark.asyncio
@pytest.mark.parametrize("exception", [ValueError("An error"), ApiException(status=502, reason="")])
async def test_non_400_error_should_be_propagated_and_call_stop_tasks(df_loop, listener, exception):
    df_loop.read_datafeed.side_effect = exception

    with pytest.raises(type(exception)) as raised_exception:
        await df_loop.start()
        assert raised_exception == exception

    df_loop.prepare_datafeed.assert_called_once()
    df_loop.read_datafeed.assert_called_once()
    df_loop.recreate_datafeed.assert_not_called()
    df_loop._stop_listener_tasks.assert_called_once()

    # assert no interaction with the listener
    assert len(listener.method_calls) == 0


@pytest.mark.asyncio
async def test_error_in_prepare_should_be_propagated(df_loop, listener):
    exception = ValueError("error")

    df_loop.prepare_datafeed.side_effect = exception

    with pytest.raises(ValueError) as raised_exception:
        await df_loop.start()
        assert raised_exception == exception

    df_loop.prepare_datafeed.assert_called_once()
    df_loop.read_datafeed.assert_not_called()
    df_loop.recreate_datafeed.assert_not_called()

    # assert no interaction with the listener
    assert len(listener.method_calls) == 0


@pytest.mark.asyncio
async def test_none_ignored_in_handle_events(df_loop, listener):
    await handle_events_and_wait_for_completion(df_loop, None)

    assert len(listener.method_calls) == 0


@pytest.mark.asyncio
async def test_empty_list_ignored_in_handle_events(df_loop, listener):
    await handle_events_and_wait_for_completion(df_loop, [])

    assert len(listener.method_calls) == 0


@pytest.mark.asyncio
async def test_list_with_single_none_ignored_in_handle_events(df_loop, listener):
    await handle_events_and_wait_for_completion(df_loop, [None])

    assert len(listener.method_calls) == 0


@pytest.mark.asyncio
async def test_list_with_none_ignored_in_handle_events(df_loop, listener, message_sent_event, initiator):
    await handle_events_and_wait_for_completion(df_loop, [None, message_sent_event])

    listener.is_accepting_event.assert_called_once_with(message_sent_event, BOT_USER)
    listener.on_message_sent.assert_called_once_with(initiator, message_sent_event.payload.message_sent)


@pytest.mark.asyncio
async def test_unknown_event_type_ignored(df_loop, listener):
    event = V4Event(type="unknown type")

    await handle_events_and_wait_for_completion(df_loop, [event])

    assert len(listener.method_calls) == 1
    listener.is_accepting_event.assert_called_once_with(event, BOT_USER)


@pytest.mark.asyncio
async def test_handle_message_sent(df_loop, listener, initiator):
    payload = V4Payload(message_sent=V4MessageSent())
    event = V4Event(type=RealTimeEvent.MESSAGESENT.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_message_sent.assert_called_once_with(initiator, payload.message_sent)


@pytest.mark.asyncio
async def test_handle_shared_post(df_loop, listener, initiator):
    payload = V4Payload(shared_post=V4SharedPost())
    event = V4Event(type=RealTimeEvent.SHAREDPOST.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_shared_post.assert_called_once_with(initiator, payload.shared_post)


@pytest.mark.asyncio
async def test_handle_instant_message_created(df_loop, listener, initiator):
    payload = V4Payload(instant_message_created=V4InstantMessageCreated())
    event = V4Event(type=RealTimeEvent.INSTANTMESSAGECREATED.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_instant_message_created.assert_called_with(initiator, payload.instant_message_created)


@pytest.mark.asyncio
async def test_handle_room_created(df_loop, listener, initiator):
    payload = V4Payload(room_created=V4RoomCreated())
    event = V4Event(type=RealTimeEvent.ROOMCREATED.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_room_created.assert_called_with(initiator, payload.room_created)


@pytest.mark.asyncio
async def test_handle_room_updated(df_loop, listener, initiator):
    payload = V4Payload(room_updated=V4RoomUpdated())
    event = V4Event(type=RealTimeEvent.ROOMUPDATED.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_room_updated.assert_called_with(initiator, payload.room_updated)


@pytest.mark.asyncio
async def test_handle_room_deactivated(df_loop, listener, initiator):
    payload = V4Payload(room_deactivated=V4RoomDeactivated())
    event = V4Event(type=RealTimeEvent.ROOMDEACTIVATED.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_room_deactivated.assert_called_with(initiator, payload.room_deactivated)


@pytest.mark.asyncio
async def test_handle_room_reactivated(df_loop, listener, initiator):
    payload = V4Payload(room_reactivated=V4RoomReactivated())
    event = V4Event(type=RealTimeEvent.ROOMREACTIVATED.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_room_reactivated.assert_called_with(initiator, payload.room_reactivated)


@pytest.mark.asyncio
async def test_handle_user_requested_to_join_room(df_loop, listener, initiator):
    payload = V4Payload(user_requested_to_join_room=V4UserRequestedToJoinRoom())
    event = V4Event(type=RealTimeEvent.USERREQUESTEDTOJOINROOM.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_user_requested_to_join_room.assert_called_with(initiator, payload.user_requested_to_join_room)


@pytest.mark.asyncio
async def test_handle_user_joined_room(df_loop, listener, initiator):
    payload = V4Payload(user_joined_room=V4UserJoinedRoom())
    event = V4Event(type=RealTimeEvent.USERJOINEDROOM.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_user_joined_room.assert_called_with(initiator, payload.user_joined_room)


@pytest.mark.asyncio
async def test_handle_user_left_room(df_loop, listener, initiator):
    payload = V4Payload(user_left_room=V4UserLeftRoom())
    event = V4Event(type=RealTimeEvent.USERLEFTROOM.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_user_left_room.assert_called_with(initiator, payload.user_left_room)


@pytest.mark.asyncio
async def test_handle_room_member_promoted_to_owner(df_loop, listener, initiator):
    payload = V4Payload(room_member_promoted_to_owner=V4RoomMemberPromotedToOwner())
    event = V4Event(type=RealTimeEvent.ROOMMEMBERPROMOTEDTOOWNER.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_room_member_promoted_to_owner.assert_called_with(initiator, payload.room_member_promoted_to_owner)


@pytest.mark.asyncio
async def test_handle_room_member_demoted_from_owner(df_loop, listener, initiator):
    payload = V4Payload(room_member_demoted_from_owner=V4RoomMemberDemotedFromOwner())
    event = V4Event(type=RealTimeEvent.ROOMMEMBERDEMOTEDFROMOWNER.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_room_demoted_from_owner.assert_called_with(initiator, payload.room_member_demoted_from_owner)


@pytest.mark.asyncio
async def test_handle_connection_requested(df_loop, listener, initiator):
    payload = V4Payload(connection_requested=V4ConnectionRequested())
    event = V4Event(type=RealTimeEvent.CONNECTIONREQUESTED.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_connection_requested.assert_called_with(initiator, payload.connection_requested)


@pytest.mark.asyncio
async def test_handle_connection_accepted(df_loop, listener, initiator):
    payload = V4Payload(connection_accepted=V4ConnectionAccepted())
    event = V4Event(type=RealTimeEvent.CONNECTIONACCEPTED.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_connection_accepted.assert_called_with(initiator, payload.connection_accepted)


@pytest.mark.asyncio
async def test_handle_message_suppressed(df_loop, listener, initiator):
    payload = V4Payload(message_suppressed=V4MessageSuppressed())
    event = V4Event(type=RealTimeEvent.MESSAGESUPPRESSED.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_message_suppressed.assert_called_with(initiator, payload.message_suppressed)


@pytest.mark.asyncio
async def test_handle_symphony_element(df_loop, listener, initiator):
    payload = V4Payload(symphony_elements_action=V4SymphonyElementsAction())
    event = V4Event(type=RealTimeEvent.SYMPHONYELEMENTSACTION.name, payload=payload, initiator=initiator)

    await handle_events_and_wait_for_completion(df_loop, [event])

    listener.is_accepting_event.assert_called_with(event, BOT_USER)
    listener.on_symphony_elements_action.assert_called_once_with(initiator, payload.symphony_elements_action)


@pytest.mark.asyncio
async def test_listener_concurrency(bare_df_loop, read_df_side_effect):
    class QueueListener(RealTimeEventListener):
        def __init__(self, queue, other_queue):
            self.queue = queue
            self.other_queue = other_queue
            self.first = True

        async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
            if self.first:
                await self.queue.put("message")
                await self.other_queue.get()
                await bare_df_loop.stop()
            self.first = False

    bare_df_loop.read_datafeed.side_effect = read_df_side_effect

    queue_one = asyncio.Queue()
    queue_two = asyncio.Queue()

    bare_df_loop.subscribe(QueueListener(queue_one, queue_two))
    bare_df_loop.subscribe(QueueListener(queue_two, queue_one))

    await bare_df_loop.start()  # test it finishes without deadlock


@pytest.mark.asyncio
async def test_events_concurrency(bare_df_loop, read_df_side_effect):
    class QueueListener(RealTimeEventListener):
        def __init__(self):
            self.queue = asyncio.Queue()
            self.count = 0

        async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
            self.count += 1
            if self.count == 1:
                await self.queue.get()
                await bare_df_loop.stop()
            elif self.count == 2:
                await self.queue.put("message")

    bare_df_loop.read_datafeed.side_effect = read_df_side_effect
    bare_df_loop.subscribe(QueueListener())

    await bare_df_loop.start()  # test no deadlock
