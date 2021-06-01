from unittest.mock import MagicMock, AsyncMock

import pytest
from symphony.bdk.gen.agent_model.v4_user import V4User

from symphony.bdk.core.activity.command import CommandActivity, SlashCommandActivity
from symphony.bdk.core.activity.form import FormReplyActivity
from symphony.bdk.core.activity.registry import ActivityRegistry
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message import V4Message
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent
from symphony.bdk.gen.agent_model.v4_stream import V4Stream
from symphony.bdk.core.activity.user_joined_room import UserJoinedRoomActivity
from symphony.bdk.gen.agent_model.v4_user_joined_room import V4UserJoinedRoom
from symphony.bdk.gen.agent_model.v4_symphony_elements_action import V4SymphonyElementsAction


@pytest.fixture(name="session_service")
def fixture_session_service():
    session_service = MagicMock(SessionService)
    session_service.get_session = AsyncMock()
    return session_service


@pytest.fixture(name="command")
def fixture_command():
    return MagicMock(CommandActivity)


@pytest.fixture(name="form")
def fixture_form():
    return MagicMock(FormReplyActivity)


@pytest.fixture(name="user")
def fixture_user():
    return MagicMock(UserJoinedRoomActivity)


@pytest.fixture(name="message_sent")
def fixture_message_sent():
    return V4MessageSent(message=V4Message(message_id="message_id",
                                           message="<div><p><span>hello world</span></p></div>",
                                           stream=V4Stream(stream_id="stream_id")))


@pytest.fixture(name="elements_action")
def fixture_elements_action():
    return V4SymphonyElementsAction(form_id="test_form",
                                    form_values={"key": "value"})


@pytest.fixture(name="user_joined_room")
def fixture_user_joined_room():
    return V4UserJoinedRoom(stream=V4Stream(stream_id="12345678"),
                            affected_user=V4User(user_id=0))


@pytest.fixture(name="activity_registry")
def fixture_activity_registry(session_service):
    return ActivityRegistry(session_service)


@pytest.mark.asyncio
async def test_register(activity_registry, session_service, message_sent):
    # call on_message_sent a first time
    await activity_registry.on_message_sent(V4Initiator(), message_sent)
    session_service.get_session.assert_called_once()

    session_service.get_session.reset_mock()
    # call on_message_sent a second time, get_session() is not performed twice
    await activity_registry.on_message_sent(V4Initiator(), message_sent)
    session_service.get_session.assert_not_called()


@pytest.mark.asyncio
async def test_register_different_activities_instance(activity_registry, command, form, user, message_sent,
                                                      elements_action, user_joined_room):
    command.on_activity = AsyncMock()
    form.on_activity = AsyncMock()
    user.on_activity = AsyncMock()

    activity_registry.register(command)
    activity_registry.register(form)
    activity_registry.register(user)

    assert len(activity_registry._activity_list) == 3

    await activity_registry.on_message_sent(V4Initiator(), message_sent)

    command.before_matcher.assert_called_once()
    form.before_matcher.assert_not_called()
    user.before_matcher.assert_not_called()

    command.reset_mock()
    form.reset_mock()
    user.reset_mock()

    await activity_registry.on_symphony_elements_action(V4Initiator(), elements_action)

    form.before_matcher.assert_called_once()
    command.before_matcher.assert_not_called()
    user.before_matcher.assert_not_called()

    command.reset_mock()
    form.reset_mock()
    user.reset_mock()

    await activity_registry.on_user_joined_room(V4Initiator(), user_joined_room)

    user.before_matcher.assert_called_once()
    form.before_matcher.assert_not_called()
    command.before_matcher.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_sent(activity_registry, message_sent, command):
    command.on_activity = AsyncMock()

    activity_registry.register(command)
    await activity_registry.on_message_sent(V4Initiator(), message_sent)

    assert len(activity_registry._activity_list) == 1

    command.before_matcher.assert_called_once()
    command.matches.assert_called_once()
    command.on_activity.assert_called_once()


@pytest.mark.asyncio
async def test_on_message_sent_false_match(activity_registry, message_sent, command):
    command.on_activity = AsyncMock()

    command.matches.return_value = False

    activity_registry.register(command)
    await activity_registry.on_message_sent(V4Initiator(), message_sent)

    command.before_matcher.assert_called_once()
    command.matches.assert_called_once()
    command.on_activity.assert_not_called()


@pytest.mark.asyncio
async def test_on_symphony_elements_action(activity_registry, elements_action, form):
    form.on_activity = AsyncMock()

    activity_registry.register(form)
    await activity_registry.on_symphony_elements_action(V4Initiator(), elements_action)

    assert len(activity_registry._activity_list) == 1

    form.before_matcher.assert_called_once()
    form.matches.assert_called_once()
    form.on_activity.assert_called_once()


@pytest.mark.asyncio
async def test_on_symphony_elements_action_false_match(activity_registry, elements_action, form):
    form.on_activity = AsyncMock()
    form.matches.return_value = False

    activity_registry.register(form)
    await activity_registry.on_symphony_elements_action(V4Initiator(), elements_action)

    form.before_matcher.assert_called_once()
    form.matches.assert_called_once()
    form.on_activity.assert_not_called()


@pytest.mark.asyncio
async def test_on_user_joined_room(activity_registry, user_joined_room, user):
    user.on_activity = AsyncMock()

    activity_registry.register(user)
    await activity_registry.on_user_joined_room(V4UserJoinedRoom, user_joined_room)

    assert len(activity_registry._activity_list) == 1

    user.before_matcher.assert_called_once()
    user.matches.assert_called_once()
    user.on_activity.assert_called_once()


@pytest.mark.asyncio
async def test_on_user_joined_room_false_match(activity_registry, user_joined_room, user):
    user.on_activity = AsyncMock()

    user.matches.return_value = False

    activity_registry.register(user)
    await activity_registry.on_user_joined_room(V4Initiator(), user_joined_room)

    user.before_matcher.assert_called_once()
    user.matches.assert_called_once()
    user.on_activity.assert_not_called()


@pytest.mark.asyncio
async def test_slash_command_decorator(activity_registry, message_sent):
    @activity_registry.slash("/command")
    async def listener(context):
        pass

    assert len(activity_registry._activity_list) == 1
    assert isinstance(activity_registry._activity_list[0], SlashCommandActivity)


@pytest.mark.asyncio
async def test_slash_command(activity_registry, message_sent):
    listener = AsyncMock()
    mention_bot = False
    command_name = "/command"

    activity_registry.slash(command_name, mention_bot)(listener)

    assert len(activity_registry._activity_list) == 1

    slash_activity = activity_registry._activity_list[0]
    assert isinstance(slash_activity, SlashCommandActivity)
    assert slash_activity._name == command_name
    assert slash_activity._requires_mention_bot == mention_bot
    assert slash_activity._callback == listener


@pytest.mark.asyncio
async def test_slash_same_command_name_and_mention(activity_registry, message_sent):
    listener1 = AsyncMock()
    listener2 = AsyncMock()
    mention_bot = True
    command_name = "/command"

    activity_registry.slash(command_name, mention_bot)(listener1)
    activity_registry.slash(command_name, mention_bot)(listener2)

    assert len(activity_registry._activity_list) == 1

    slash_activity = activity_registry._activity_list[0]
    assert isinstance(slash_activity, SlashCommandActivity)
    assert slash_activity._name == command_name
    assert slash_activity._requires_mention_bot
    assert slash_activity._callback == listener2


@pytest.mark.asyncio
async def test_slash_same_command_name_different_mention(activity_registry, message_sent):
    listener1 = AsyncMock()
    listener2 = AsyncMock()
    command_name = "/command"

    activity_registry.slash(command_name, True)(listener1)
    activity_registry.slash(command_name, False)(listener2)

    assert len(activity_registry._activity_list) == 2
    slash_activity1 = activity_registry._activity_list[0]
    assert isinstance(slash_activity1, SlashCommandActivity)
    assert slash_activity1._name == command_name
    assert slash_activity1._requires_mention_bot
    assert slash_activity1._callback == listener1
    slash_activity2 = activity_registry._activity_list[1]
    assert isinstance(slash_activity2, SlashCommandActivity)
    assert slash_activity2._name == command_name
    assert not slash_activity2._requires_mention_bot
    assert slash_activity2._callback == listener2

