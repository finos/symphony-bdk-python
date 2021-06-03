from symphony.bdk.core.activity.command import CommandContext, SlashCommandActivity
from symphony.bdk.core.symphony_bdk import SymphonyBdk


class HelpCommand(SlashCommandActivity):
    """The help command is a particular CommandActivity which returns the list of all commands available for the
    specific bot
    The Slash command is triggered if we receive a MESSAGESENT event with message text:
      - "@{bot_display name} /help"
    """

    def __init__(self, bdk: SymphonyBdk):
        super().__init__("/help", True, None, "List available commands")
        self._bdk = bdk

    async def on_activity(self, context: CommandContext):
        activity_list = self._bdk.activities().activity_list
        help_message = ""
        for act in activity_list:
            help_message += "<li>" + act.name + " - " + act.build_command_description() + "</li>"
        await self._bdk.messages().send_message(context.stream_id,
                                                "<messageML><ul>" + help_message + "</ul></messageML>")
