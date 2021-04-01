from unittest.mock import MagicMock, AsyncMock

import pytest

from symphony.bdk.core.activity.command import CommandActivity
from symphony.bdk.core.activity.form import FormReplyActivity
from symphony.bdk.core.activity.registry import ActivityRegistry
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message import V4Message
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_stream import V4Stream
from symphony.bdk.gen.agent_model.v4_symphony_elements_action import V4SymphonyElementsAction


@pytest.fixture(name="session_service")
def fixture_session_service():
    return MagicMock(SessionService)


@pytest.fixture(name="command")
def fixture_command():
    return MagicMock(CommandActivity)


@pytest.fixture(name="form")
def fixture_form():
    return MagicMock(FormReplyActivity)


@pytest.fixture(name="message_sent")
def fixture_message_sent():
    return V4MessageSent(message=V4Message(message_id="message_id",
                                           message="<div><p><span>hello world</span></p></div>",
                                           stream=V4Stream(stream_id="stream_id")))


@pytest.fixture(name="elements_action")
def fixture_elements_action():
    return V4SymphonyElementsAction(form_id="test_form",
                                    form_values={"key": "value"})


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
async def test_register_different_activities_instance(activity_registry, command, form, message_sent, elements_action):
    command.on_activity = AsyncMock()
    form.on_activity = AsyncMock()

    await activity_registry.register(command)
    await activity_registry.register(form)

    assert len(activity_registry._activity_list) == 2

    await activity_registry.on_message_sent(V4Initiator(), message_sent)

    command.before_matcher.assert_called_once()
    form.before_matcher.assert_not_called()

    command.reset_mock()
    form.reset_mock()

    await activity_registry.on_symphony_elements_action(V4Initiator(), elements_action)

    form.before_matcher.assert_called_once()
    command.before_matcher.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_sent(activity_registry, message_sent, command):
    command.on_activity = AsyncMock()

    await activity_registry.register(command)
    await activity_registry.on_message_sent(V4Initiator(), message_sent)

    assert len(activity_registry._activity_list) == 1

    command.before_matcher.assert_called_once()
    command.matches.assert_called_once()
    command.on_activity.assert_called_once()


@pytest.mark.asyncio
async def test_on_message_sent_false_match(activity_registry, message_sent, command):
    command.on_activity = AsyncMock()

    command.matches.return_value = False

    await activity_registry.register(command)
    await activity_registry.on_message_sent(V4Initiator(), message_sent)

    command.before_matcher.assert_called_once()
    command.matches.assert_called_once()
    command.on_activity.assert_not_called()


@pytest.mark.asyncio
async def test_on_symphony_elements_action(activity_registry, elements_action, form):
    form.on_activity = AsyncMock()

    await activity_registry.register(form)
    await activity_registry.on_symphony_elements_action(V4Initiator(), elements_action)

    assert len(activity_registry._activity_list) == 1

    form.before_matcher.assert_called_once()
    form.matches.assert_called_once()
    form.on_activity.assert_called_once()


@pytest.mark.asyncio
async def test_on_symphony_elements_action_false_match(activity_registry, elements_action, form):
    form.on_activity = AsyncMock()
    form.matches.return_value = False

    await activity_registry.register(form)
    await activity_registry.on_symphony_elements_action(V4Initiator(), elements_action)

    form.before_matcher.assert_called_once()
    form.matches.assert_called_once()
    form.on_activity.assert_not_called()
