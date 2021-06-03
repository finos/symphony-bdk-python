from unittest.mock import AsyncMock, MagicMock

import pytest

from symphony.bdk.core.activity.command import SlashCommandActivity, CommandContext
from symphony.bdk.core.activity.help_command import HelpCommand
from symphony.bdk.core.activity.registry import ActivityRegistry
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message import V4Message
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_stream import V4Stream

STREAM_ID = "stream_id"


@pytest.fixture(name="session_service")
def fixture_session_service():
    session_service = MagicMock(SessionService)
    session_service.get_session = AsyncMock()
    return session_service


@pytest.fixture(name="activity_registry")
def fixture_activity_registry(session_service):
    return ActivityRegistry(session_service)


@pytest.fixture(name="bdk")
def fixture_bdk(activity_registry):
    bdk = MagicMock(SymphonyBdk)
    bdk.activities.return_value = activity_registry
    bdk.messages.return_value = MagicMock(MessageService)
    bdk.messages.send_message = AsyncMock()
    return bdk


@pytest.fixture(name="command_context")
def fixture_command_context():
    message_content = "<messageML>@bot_name /help</messageML>"
    message_sent = V4MessageSent(message=V4Message(message_id="message_id",
                                                   message=message_content,
                                                   stream=V4Stream(stream_id=STREAM_ID)))
    return CommandContext(V4Initiator(), message_sent, "bot_name")


@pytest.mark.asyncio
async def test_help_command(bdk, activity_registry, command_context):
    listener = AsyncMock()

    activity_registry.slash("/hello")(listener)
    activity_registry.register(HelpCommand(bdk))

    assert len(activity_registry.activity_list) == 2
    help_activity = activity_registry.activity_list[1]
    assert isinstance(help_activity, HelpCommand)
    assert help_activity.matches(command_context)
    await help_activity.on_activity(command_context)
    message = "<messageML><ul><li>/hello -  (mention required)</li>" \
              "<li>/help - List available commands (mention required)</li></ul></messageML>"
    bdk.messages().send_message.assert_called_once_with(STREAM_ID, message)


@pytest.mark.asyncio
async def test_help_command_no_other_commands_found(bdk, activity_registry, command_context):
    activity_registry.register(HelpCommand(bdk))

    assert len(activity_registry.activity_list) == 1
    help_activity = activity_registry.activity_list[0]
    assert isinstance(help_activity, HelpCommand)
    assert help_activity.matches(command_context)
    await help_activity.on_activity(command_context)
    message = "<messageML><ul><li>/help - List available commands (mention required)</li></ul></messageML>"
    bdk.messages().send_message.assert_called_once_with(STREAM_ID, message)


@pytest.mark.asyncio
async def test_override_help_command_with_slash_help(bdk, activity_registry, command_context):
    listener = AsyncMock()

    activity_registry.slash("/help")(listener)
    activity_registry.register(HelpCommand(bdk))

    assert len(activity_registry.activity_list) == 1
    help_activity = activity_registry.activity_list[0]
    assert isinstance(help_activity, HelpCommand)
    assert help_activity.matches(command_context)
    await help_activity.on_activity(command_context)
    message = "<messageML><ul><li>/help - List available commands (mention required)</li></ul></messageML>"
    bdk.messages().send_message.assert_called_once_with(STREAM_ID, message)


@pytest.mark.asyncio
async def test_override_slash_help_with_help_command(bdk, activity_registry, command_context):
    listener = AsyncMock()

    activity_registry.register(HelpCommand(bdk))
    activity_registry.slash("/help")(listener)

    assert len(activity_registry.activity_list) == 1
    help_activity = activity_registry.activity_list[0]
    assert isinstance(help_activity, SlashCommandActivity)
    assert help_activity.matches(command_context)
    await help_activity.on_activity(command_context)
    bdk.messages.send_message.assert_not_called()
    help_activity._callback.assert_called_once_with(command_context)
