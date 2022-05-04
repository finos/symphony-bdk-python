import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from tests.core.service.datafeed.test_fixtures import fixture_initiator_userid, fixture_session_service, \
    fixture_message_sent_v4_event

from symphony.bdk.gen.agent_model.v5_event_list import V5EventList
from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.service.datafeed.abstract_ackId_event_loop import AbstractAckIdEventLoop
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi


@pytest.fixture(name="read_events_side_effect")
def fixture_read_events_side_effect(message_sent_v4_event):
    async def read_events(**kwargs):
        await asyncio.sleep(0.001)  # to force the switching of tasks
        events_list = V5EventList()
        events_list.ack_id = "testing_ack_id"
        events_list.events = [message_sent_v4_event]
        return events_list

    return read_events


@pytest.fixture(name="bare_ackid_event_loop")
def fixture_bare_df_loop(session_service):
    # patch.multiple called in order to be able to instantiate AbstractDatafeedLoop
    with patch.multiple(AbstractAckIdEventLoop, __abstractmethods__=set()):
        mock_df = AbstractAckIdEventLoop(DatafeedApi(AsyncMock()), session_service, None, BdkConfig())
        mock_df._read_events = AsyncMock()
        mock_df._run_listener_tasks = AsyncMock()
        return mock_df


@pytest.mark.asyncio
async def test_run_loop_iteration(bare_ackid_event_loop, read_events_side_effect):
    bare_ackid_event_loop._read_events.side_effect = read_events_side_effect
    await bare_ackid_event_loop._run_loop_iteration()
    assert bare_ackid_event_loop._ack_id == "testing_ack_id"
