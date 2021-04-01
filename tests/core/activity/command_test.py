import pytest

from symphony.bdk.core.activity.command import CommandActivity, CommandContext
from symphony.bdk.core.activity.exception import FatalActivityExecutionException
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message import V4Message
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_stream import V4Stream


@pytest.fixture(name="activity")
def fixture_activity():
    class TestCommandActivity(CommandActivity):
        """Dummy test command activity"""
        pass

    return TestCommandActivity()


def test_matcher(activity):
    context = CommandContext(V4Initiator(),
                             V4MessageSent(message=V4Message(message_id="message_id",
                                                             message="<div><p><span>hello world</span></p></div>",
                                                             stream=V4Stream(stream_id="stream_id"))),
                             "bot_name")

    def dummy_matcher(passed_context: CommandContext):
        return passed_context.text_content.startswith("foobar")

    activity.matches = dummy_matcher

    context._text_content = "foobar"
    assert activity.matches(context)

    context._text_content = "barfoo"
    assert not activity.matches(context)


def test_context_with_valid_message(activity):
    message = "<div><p><span>hello world</span></p></div>"
    context = CommandContext(V4Initiator(),
                             V4MessageSent(message=V4Message(message_id="message_id",
                                                             message=message,
                                                             stream=V4Stream(stream_id="stream_id"))),
                             "bot_name")
    assert context.text_content == "hello world"


def test_context_with_invalid_message(activity):
    message = "<div<p><span>hello world<span></p></div>"  # Bad xml format, missing chevron
    with pytest.raises(FatalActivityExecutionException):
        CommandContext(V4Initiator(),
                       V4MessageSent(message=V4Message(message_id="message_id",
                                                       message=message,
                                                       stream=V4Stream(stream_id="stream_id"))),
                       "bot_name")
