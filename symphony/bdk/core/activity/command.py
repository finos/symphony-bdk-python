import logging

from symphony.bdk.core.activity.api import AbstractActivity, ActivityContext
from symphony.bdk.core.service.message.message_parser import get_text_content_from_message
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent

logger = logging.getLogger(__name__)


class CommandContext(ActivityContext[V4MessageSent]):
    """
    Default implementation of the :py:class:`ActivityContext` handled by the :py:class:`CommandActivity`.
    """
    def __init__(self, initiator: V4Initiator, source_event: V4MessageSent, bot_display_name: str):
        self._message_id = source_event.message.message_id
        self._stream_id = source_event.message.stream.stream_id
        self._bot_display_name = bot_display_name
        self._text_content = ""
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
    """
    A command activity corresponds to any message send in a chat where the bot is part of.
    """
    def __init__(self):
        self.bot_display_name = str

    def matches(self, context: CommandContext) -> bool:
        pass

    def on_activity(self, context: CommandContext):
        pass

    def before_matcher(self, context: CommandContext):
        context._text_content = get_text_content_from_message(context.source_event.message)

# FIXME?
# class SlashCommand(CommandActivity):
#
#     def __init__(self, slash_cmd_name: str, func, requires_bot_mention: bool = True):
#         self._slash_cmd_name = slash_cmd_name
#         self._requires_bot_mention = requires_bot_mention
#         self._func = func
#         super().__init__()
#
#     def matches(self, context: CommandContext) -> bool:
#         cmd_prefix = ""
#         if self._requires_bot_mention:
#             cmd_prefix = "@" + context.bot_display_name + " "
#         return context.text_content.startswith(cmd_prefix + self._slash_cmd_name)
#
#     async def on_activity(self, context: CommandContext):
#         await self._func(context)
#
#
# def slash(cmd_name: str, func):
#     return SlashCommand(cmd_name, func)

