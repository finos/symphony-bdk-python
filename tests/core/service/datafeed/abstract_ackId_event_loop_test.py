import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.service.datafeed.abstract_ackId_event_loop import AbstractAckIdEventLoop
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.gen.pod_model.user_v2 import UserV2
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_user import V4User
from symphony.bdk.gen.agent_model.v4_message import V4Message
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_payload import V4Payload
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import RealTimeEvent
from symphony.bdk.gen.agent_model.v4_event import V4Event
from symphony.bdk.gen.agent_model.v5_event_list import V5EventList

BOT_USER_ID = 12345
BOT_INFO = UserV2(id=BOT_USER_ID)


@pytest.fixture(name="initiator")
def fixture_initiator():
    return V4Initiator(user=V4User(user_id=67890))


@pytest.fixture(name="message_sent_event")
def fixture_message_sent_event(initiator):
    payload = V4Payload(message_sent=V4MessageSent(message=V4Message(message="message")))
    return V4Event(type=RealTimeEvent.MESSAGESENT.name, payload=payload, initiator=initiator)


@pytest.fixture(name="session_service")
def fixture_session_service():
    session_service = AsyncMock()
    session_service.get_session.return_value = BOT_INFO
    return session_service


@pytest.fixture(name="bare_ackid_event_loop")
def fixture_bare_df_loop(session_service):
    # patch.multiple called in order to be able to instantiate AbstractDatafeedLoop
    with patch.multiple(AbstractAckIdEventLoop, __abstractmethods__=set()):
        mock_df = AbstractAckIdEventLoop(DatafeedApi(AsyncMock()), session_service, None, BdkConfig())
        mock_df._read_events = AsyncMock()
        mock_df._run_listener_tasks = AsyncMock()
        return mock_df


@pytest.fixture(name="read_events_side_effect")
def fixture_read_events_side_effect(message_sent_event):
    async def read_events(**kwargs):
        await asyncio.sleep(0.001)  # to force the switching of tasks
        events_list = V5EventList()
        events_list.ack_id = "testing_ack_id"
        events_list.events = [message_sent_event]
        return events_list

    return read_events


@pytest.mark.asyncio
async def test_recreate_datafeed(bare_ackid_event_loop):
    bare_ackid_event_loop._ack_id = "not_empty_ack_id"
    await bare_ackid_event_loop.recreate_datafeed()
    assert bare_ackid_event_loop._ack_id is ""


@pytest.mark.asyncio
async def test_run_loop_iteration(bare_ackid_event_loop, read_events_side_effect):
    bare_ackid_event_loop._read_events.side_effect = read_events_side_effect
    await bare_ackid_event_loop._run_loop_iteration()
    assert bare_ackid_event_loop._ack_id == "testing_ack_id"
