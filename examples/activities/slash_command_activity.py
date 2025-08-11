import asyncio
import logging.config
from pathlib import Path

from symphony.bdk.core.activity.command import CommandContext
from symphony.bdk.core.activity.help_command import HelpCommand
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    async with SymphonyBdk(
        BdkConfigLoader.load_from_symphony_dir("config.yaml")
    ) as bdk:
        activities = bdk.activities()
        messages = bdk.messages()

        @activities.slash("/hello")
        async def on_hello(context: CommandContext):
            await messages.send_message(
                context.stream_id, "<messageML>Hello, World!</messageML>"
            )

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
