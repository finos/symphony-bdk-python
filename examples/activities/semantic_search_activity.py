import asyncio
import html
import logging.config
from pathlib import Path

from symphony.bdk.core.activity.command import CommandActivity, CommandContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    async with SymphonyBdk(BdkConfigLoader.load_from_symphony_dir("config.yaml")) as bdk:
        bdk.activities().register(SemanticSearchCommandActivity(bdk.messages()))
        await bdk.datafeed().start()


class SemanticSearchCommandActivity(CommandActivity):
    """Handles "/search <free-text query>" and replies with the matching messages found by
    :func:`MessageService.search_messages_semantic`.

    This is written as a plain CommandActivity rather than with the activities.slash decorator
    because a slash-command {argument} only ever binds a single whitespace-delimited token - it
    can't capture a free-text, multi-word query like "/search green investments".
    """

    def __init__(self, messages: MessageService):
        self._messages = messages
        super().__init__()

    def matches(self, context: CommandContext) -> bool:
        return context.text_content.startswith("/search ")

    async def on_activity(self, context: CommandContext):
        query = context.text_content[len("/search ") :].strip()
        if not query:
            return

        results = await self._messages.search_messages_semantic(query, limit=5)

        if not results:
            await self._messages.send_message(
                context.stream_id, "<messageML>No matching messages found.</messageML>"
            )
            return

        rows = "".join(
            f"<tr><td>{r.message_id}</td><td>{html.escape(r.message or '')}</td></tr>"
            for r in results
        )
        table = f"<table><tr><th>Message ID</th><th>Content</th></tr>{rows}</table>"
        await self._messages.send_message(context.stream_id, f"<messageML>{table}</messageML>")


logging.config.fileConfig(
    Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False
)

try:
    logging.info("Running activity example...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending activity example")
