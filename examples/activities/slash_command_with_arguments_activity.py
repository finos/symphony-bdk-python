import asyncio
import logging.config
from pathlib import Path

from symphony.bdk.core.activity.command import CommandContext
from symphony.bdk.core.activity.help_command import HelpCommand
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    async with SymphonyBdk(BdkConfigLoader.load_from_symphony_dir("config.yaml")) as bdk:
        activities = bdk.activities()
        messages = bdk.messages()

        @activities.slash("/echo {@mention_argument}")
        async def on_echo_mention(context: CommandContext):
            mentioned_user = context.arguments.get_mention("mention_argument")
            message = (
                f"Mentioned user: {mentioned_user.user_display_name}, id: {mentioned_user.user_id}"
            )

            await messages.send_message(context.stream_id, f"<messageML>{message}</messageML>")

        @activities.slash("/echo {#hashtag_argument}")
        async def on_echo_hashtag(context: CommandContext):
            hashtag = context.arguments.get_hashtag("hashtag_argument")
            message = f"Hashtag value: {hashtag.value}"

            await messages.send_message(context.stream_id, f"<messageML>{message}</messageML>")

        @activities.slash("/echo {$cashtag_argument}")
        async def on_echo_cashtag(context: CommandContext):
            cashtag = context.arguments.get_cashtag("cashtag_argument")
            message = f"Cashtag value: {cashtag.value}"

            await messages.send_message(context.stream_id, f"<messageML>{message}</messageML>")

        @activities.slash("/echo {first_string_argument} {second_string_argument}")
        async def on_echo_string_arguments(context: CommandContext):
            # Get string argument with get_string
            first_string_argument = context.arguments.get_string("first_string_argument")

            # Get string argument with get_as_string
            second_string_argument = context.arguments.get_as_string("second_string_argument")

            message = f"Received arguments: {first_string_argument} and {second_string_argument}"

            await messages.send_message(context.stream_id, f"<messageML>{message}</messageML>")

        bdk.activities().register(HelpCommand(bdk))

        await bdk.datafeed().start()


logging.config.fileConfig(
    Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False
)

try:
    logging.info("Running activity example...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending activity example")
