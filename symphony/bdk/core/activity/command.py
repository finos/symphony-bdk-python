import logging
import re

from symphony.bdk.core.activity.api import AbstractActivity, ActivityContext
from symphony.bdk.core.activity.exception import FatalActivityExecutionException
from symphony.bdk.core.service.exception import MessageParserError
from symphony.bdk.core.service.message.message_parser import get_text_content_from_message
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent

logger = logging.getLogger(__name__)


class CommandContext(ActivityContext[V4MessageSent]):
    """Default implementation of the :py:class:`ActivityContext` handled by the :py:class:`CommandActivity`.
    """

    def __init__(self, initiator: V4Initiator, source_event: V4MessageSent, bot_display_name: str):
        self._message_id = source_event.message.message_id
        self._stream_id = source_event.message.stream.stream_id
        self._bot_display_name = bot_display_name
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


class CommandActivity(AbstractActivity[CommandContext]):
    """A command activity corresponds to any message sent in a chat where the bot is part of.
    """

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

    def __init__(self, name, requires_mention_bot, callback):
        """

        :param name: the command name
        :param requires_mention_bot: if the command requires the bot mention to trigger the slash command
        :param callback: the coroutine to be executed if message text matches
        """
        self._name = name
        self._requires_mention_bot = requires_mention_bot
        self._callback = callback

    def matches(self, context: CommandContext) -> bool:
        pattern = rf"@{context.bot_display_name} {self._name}" if self._requires_mention_bot else rf"{self._name}"
        return pattern == context.text_content

    async def on_activity(self, context: CommandContext):
        await self._callback(context)
