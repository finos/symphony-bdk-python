from unittest.mock import AsyncMock

import pytest

from symphony.bdk.core.activity.command import (
    CommandActivity,
    CommandContext,
    SlashCommandActivity,
)
from symphony.bdk.core.activity.exception import FatalActivityExecutionException
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message import V4Message
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_stream import V4Stream

BOT_NAME = "bot_name"
BOT_USER_ID = 123456789

STREAM_ID = "stream_id"
MESSAGE_ID = "message_id"
HELLO_WORLD_MESSAGE = "hello world"


@pytest.fixture(name="activity")
def fixture_activity():
    class TestCommandActivity(CommandActivity):
        """Dummy test command activity"""

    return TestCommandActivity()


@pytest.fixture(name="message_sent")
def fixture_message_sent():
    return create_message_sent(f"<div><p><span>{HELLO_WORLD_MESSAGE}</span></p></div>")


def create_command_context(message_sent):
    return create_command_context_with_bot_id(message_sent, BOT_USER_ID)


def create_command_context_with_bot_id(message_sent, bot_id):
    return CommandContext(V4Initiator(), message_sent, BOT_NAME, bot_id)


def create_message_sent(message):
    return create_message_sent_with_data(message)


def create_message_sent_with_data(content, data="{}"):
    return V4MessageSent(
        message=V4Message(
            attachments=[],
            message_id=MESSAGE_ID,
            message='<div data-format="PresentationML" data-version="2.0" class="wysiwyg"><p>'
            + content
            + "</p></div>",
            stream=V4Stream(stream_id=STREAM_ID),
            data=data,
        )
    )


def test_matcher(activity, message_sent):
    context = create_command_context(message_sent)

    def dummy_matcher(passed_context: CommandContext):
        return passed_context.text_content.startswith("foobar")

    activity.matches = dummy_matcher

    context._text_content = "foobar"
    assert activity.matches(context)

    context._text_content = "barfoo"
    assert not activity.matches(context)


def test_context_with_valid_message(activity, message_sent):
    context = create_command_context(message_sent)
    assert context.text_content == "hello world"


def test_context_with_invalid_message(activity):
    message = (
        "<div<p><span>hello world<span></p></div>"  # Bad xml format, missing chevron
    )
    with pytest.raises(FatalActivityExecutionException):
        create_command_context(create_message_sent(message))


def test_command_context(message_sent):
    initiator = V4Initiator()
    context = CommandContext(initiator, message_sent, BOT_NAME, BOT_USER_ID)

    assert context.initiator == initiator
    assert context.source_event == message_sent
    assert context.bot_display_name == BOT_NAME
    assert context.bot_user_id == BOT_USER_ID
    assert context.text_content == HELLO_WORLD_MESSAGE
    assert context.message_id == MESSAGE_ID
    assert context.stream_id == STREAM_ID
    assert context.arguments is None


def test_slash_command_matches_with_bot_mention():
    command = "/command"
    other_command = "/other_command"
    other_bot_user_id = 123000
    slash_command = SlashCommandActivity(command, True, AsyncMock())

    # The bot user id is set in runtime in a lazy way
    slash_command.bot_user_id = BOT_USER_ID

    context = create_command_context(
        create_message_sent_with_data(
            content=f'<div><p><span class="entity" data-entity-id="0">'
            f"@{BOT_NAME}</span>{command}</p></div>",
            data=f'{{"0":{{"id":[{{"type":"com.symphony.user.userId","value":"{BOT_USER_ID}"}}],'
            '"type":"com.symphony.user.mention"}}',
        )
    )
    assert slash_command.matches(context)

    context = create_command_context(
        create_message_sent_with_data(
            content=f'<div><p><span class="entity" data-entity-id="0">'
            f"@{BOT_NAME}</span>{other_command}</p></div>",
            data=f'{{"0":{{"id":[{{"type":"com.symphony.user.userId","value":"{BOT_USER_ID}"}}],'
            '"type":"com.symphony.user.mention"}}',
        )
    )
    assert not slash_command.matches(context)

    context = create_command_context(
        create_message_sent_with_data(
            content=f'<div><p><span class="entity" data-entity-id="0">'
            f"@other_bot_name</span>{other_command}</p></div>",
            data=f'{{"0":{{"id":[{{"type":"com.symphony.user.userId","value":"{other_bot_user_id}"}}],'
            '"type":"com.symphony.user.mention"}}',
        )
    )
    assert not slash_command.matches(context)


def test_slash_command_matches_without_bot_mention():
    command = "/command"
    other_command = "/other_command"
    slash_command = SlashCommandActivity(command, False, AsyncMock())

    context = create_command_context(
        create_message_sent_with_data(content=f"<div><p>{command}</p></div>", data="{}")
    )
    assert slash_command.matches(context)

    context = create_command_context(
        create_message_sent_with_data(
            content=f'<div><p><span class="entity" data-entity-id="0">'
            f"@{BOT_NAME}</span>{command}</p></div>",
            data=f'{{"0":{{"id":[{{"type":"com.symphony.user.userId","value":"{BOT_USER_ID}"}}],'
            '"type":"com.symphony.user.mention"}}',
        )
    )
    assert not slash_command.matches(context)

    context = create_command_context(
        create_message_sent_with_data(
            content=f"<div><p>{other_command}</p></div>", data="{}"
        )
    )
    assert not slash_command.matches(context)


@pytest.mark.asyncio
async def test_slash_command_on_activity_calls_callback(message_sent):
    listener_callback = AsyncMock()
    slash_command = SlashCommandActivity("/command", False, listener_callback)
    context = create_command_context(message_sent)

    await slash_command.on_activity(context)
    listener_callback.assert_called_once_with(context)
