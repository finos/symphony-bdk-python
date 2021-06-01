from symphony.bdk.core.activity.command import CommandContext, SlashCommandActivity
from symphony.bdk.core.activity.registry import ActivityRegistry
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.service.message.model import Message


class HelpCommand(SlashCommandActivity):
    """The help command is a particular CommandActivity which returns the list of all commands available for the
    specific bot
    The Slash command is triggered if we receive a MESSAGESENT event with message text:
      - "@{bot_display name} {name}"
    """

    def __init__(self, registry: ActivityRegistry, callback: MessageService):
        super().__init__("/help", True, callback, "List available commands")
        self._registry = registry

    def matches(self, context: CommandContext) -> bool:
        pattern = rf"@{context.bot_display_name} {self._name}"
        return pattern == context.text_content

    async def on_activity(self, context: CommandContext):
        activity_list = self._registry.activity_list
        help_message = ""
        for act in activity_list:
            if not isinstance(act, HelpCommand):
                help_message += "<li>" + act.name + " - " + act.build_command_description() + "</li>"
        if not activity_list:
            await self._callback.send_message(context.stream_id, Message("<ul>" + help_message + "</ul>"))
