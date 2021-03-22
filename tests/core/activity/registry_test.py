from unittest.mock import MagicMock, AsyncMock

import pytest

from symphony.bdk.core.activity.command import CommandActivity
from symphony.bdk.core.activity.registry import ActivityRegistry
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message import V4Message
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_stream import V4Stream


@pytest.fixture(name="session_service")
def fixture_session_service():
    return MagicMock(SessionService)


@pytest.fixture(name="command")
def fixture_command():
    return MagicMock(CommandActivity)


@pytest.fixture(name="message_sent")
def fixture_message_sent():
    msg = V4MessageSent()
    msg.message = V4Message()
    msg.message.message_id = "message_id"
    msg.message.stream = V4Stream()
    msg.message.stream.stream_id = "stream_id"
    return msg


@pytest.fixture(name="activity_registry")
def fixture_activity_registry(session_service):
    return ActivityRegistry(session_service)


@pytest.mark.asyncio
async def test_register(activity_registry, session_service):
    # add first activity
    await activity_registry.register(CommandActivity())
    assert len(activity_registry._activity_list) == 1
    session_service.get_session.assert_called_once()

    session_service.get_session.reset_mock()
    # add second activity, get_session() is not performed twice
    await activity_registry.register(CommandActivity())
    assert len(activity_registry._activity_list) == 2
    session_service.get_session.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_sent(activity_registry, message_sent, command):

    command.on_activity = AsyncMock()

    await activity_registry.register(command)
    await activity_registry.on_message_sent(V4Initiator(), message_sent)

    assert len(activity_registry._activity_list) == 1

    command.before_matcher.assert_called_once()
    command.matches.assert_called_once()
