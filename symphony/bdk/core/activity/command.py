import logging

from symphony.bdk.core.activity.api import AbstractActivity, ActivityContext
from symphony.bdk.core.activity.exception import FatalActivityExecutionException
from symphony.bdk.core.activity.parsing.arguments import Arguments
from symphony.bdk.core.activity.parsing.command_token import MatchingUserIdMentionToken
from symphony.bdk.core.activity.parsing.slash_command_pattern import SlashCommandPattern
from symphony.bdk.core.service.exception import MessageParserError
from symphony.bdk.core.service.message.message_parser import get_text_content_from_message
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent

logger = logging.getLogger(__name__)


class CommandContext(ActivityContext[V4MessageSent]):
    """Default implementation of the :py:class:`ActivityContext` handled by the :py:class:`CommandActivity`.
    """

    def __init__(self, initiator: V4Initiator, source_event: V4MessageSent, bot_display_name: str,
                 bot_user_id: int = None):
        self._message_id = source_event.message.message_id
        self._stream_id = source_event.message.stream.stream_id
        self._bot_display_name = bot_display_name
        self._bot_user_id = bot_user_id
        self._arguments = None
        try:
            self._text_content = get_text_content_from_message(source_event.message)
        except MessageParserError as exc:
            raise FatalActivityExecutionException("Unable to parse presentationML") from exc
        super().__init__(initiator, source_event)

    @property
    def message_id(self):
        return self._message_id

    @property
    def stream_id(self):
        return self._stream_id

    @property
    def text_content(self) -> str:
        return self._text_content

    @property
    def bot_display_name(self) -> str:
        return self._bot_display_name

    @property
    def bot_user_id(self) -> int:
        return self._bot_user_id

    @property
    def arguments(self) -> Arguments:
        return self._arguments


class CommandActivity(AbstractActivity[CommandContext]):
    """A command activity corresponds to any message sent in a chat where the bot is part of.
    """

    def __init__(self):
        self._bot_user_id = None

    @property
    def bot_user_id(self):
        return self._bot_user_id

    @bot_user_id.setter
    def bot_user_id(self, bot_user_id):
        self._bot_user_id = bot_user_id

    def matches(self, context: CommandContext) -> bool:
        pass

    async def on_activity(self, context: CommandContext):
        pass


class SlashCommandActivity(CommandActivity):
    """A slash command is a particular CommandActivity with three parameters:
      - the command name
      - if we should mention the bot
      - the callback function

    The Slash command is triggered if we receive a MESSAGESENT event with message text:
      - "@{bot_display name} {name}" if ``requires_mention_bot`` is True
      - "{name}" otherwise
    """

    def __init__(self, name, requires_mention_bot, callback, description=""):
        """
        :param name: the command name
        :param requires_mention_bot: if the command requires the bot mention to trigger the slash command
        :param callback: the coroutine to be executed if message text matches
        """
        super().__init__()
        self._name = name
        self._command_pattern = SlashCommandPattern(name)
        self._requires_mention_bot = requires_mention_bot
        self._callback = callback
        self._description = description

        if self._requires_mention_bot:
            # The user id will be loaded in runtime in a lazy way
            self._command_pattern.prepend_token(MatchingUserIdMentionToken(lambda: self.bot_user_id))

    @property
    def name(self) -> str:
        return self._name

    def build_command_description(self) -> str:
        return self._description + " (mention required)" if self._requires_mention_bot \
            else self._description + " (mention not required)"

    def matches(self, context: CommandContext) -> bool:
        match_result = self._command_pattern.get_match_result(context.source_event.message)

        if match_result.is_matching and match_result.arguments:
            context._arguments = match_result.arguments

        return match_result.is_matching

    async def on_activity(self, context: CommandContext):
        await self._callback(context)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, SlashCommandActivity):
            return self._name == o._name and self._requires_mention_bot == o._requires_mention_bot
        return False
