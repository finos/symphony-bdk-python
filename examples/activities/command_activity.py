import asyncio
import logging.config
from pathlib import Path

from symphony.bdk.core.activity.command import CommandActivity, CommandContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    async with SymphonyBdk(BdkConfigLoader.load_from_symphony_dir("config.yaml")) as bdk:
        bdk.activities().register(HelloCommandActivity(bdk.messages()))
        await bdk.datafeed().start()


class HelloCommandActivity(CommandActivity):
    def __init__(self, messages: MessageService):
        self._messages = messages
        super().__init__()

    def matches(self, context: CommandContext) -> bool:
        return context.text_content.startswith("@" + context.bot_display_name + " /hello")

    async def on_activity(self, context: CommandContext):
        await self._messages.send_message(context.stream_id, "<messageML>Hello, World!</messageML>")


logging.config.fileConfig(Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False)

try:
    logging.info("Running activity example...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending activity example")
