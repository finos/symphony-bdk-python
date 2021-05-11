import asyncio
import logging.config
from pathlib import Path

from symphony.bdk.core.activity.command import CommandActivity, CommandContext
from symphony.bdk.core.activity.form import FormReplyActivity, FormReplyContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    async with SymphonyBdk(BdkConfigLoader.load_from_symphony_dir("config.yaml")) as bdk:
        bdk.activities().register(SlashGifCommandActivity(bdk.messages()))
        bdk.activities().register(ReplyFormReplyActivity(bdk.messages()))
        await bdk.datafeed().start()


class SlashGifCommandActivity(CommandActivity):
    def __init__(self, messages: MessageService):
        self._messages = messages

    def matches(self, context: CommandContext) -> bool:
        return context.text_content.startswith("@" + context.bot_display_name + " /gif")

    async def on_activity(self, context: CommandContext):
        await self._messages.send_message(context.stream_id, load_gif_elements_form())


class ReplyFormReplyActivity(FormReplyActivity):
    def __init__(self, messages: MessageService):
        self.messages = messages

    def matches(self, context: FormReplyContext) -> bool:
        return context.form_id == "gif-category-form" \
               and context.get_form_value("action") == "submit" \
               and context.get_form_value("category")

    async def on_activity(self, context: FormReplyContext):
        category = context.get_form_value("category")
        await self.messages.send_message(context.source_event.stream.stream_id,
                                         "<messageML> You just submitted this category: " + category + "</messageML>")


def load_gif_elements_form():
    return (Path(__file__).parent.parent / "resources/gif.mml.xml").read_text(encoding="utf-8")


logging.config.fileConfig(Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False)

try:
    logging.info("Running activity example...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending activity example")
