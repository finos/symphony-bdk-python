import asyncio
import base64
import logging.config
from pathlib import Path

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.message.model import Message
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.message_search_query import MessageSearchQuery
from symphony.bdk.gen.agent_model.v4_imported_message import V4ImportedMessage
from symphony.bdk.gen.agent_model.v4_imported_message_attachment import (
    V4ImportedMessageAttachment,
)


async def run():
    stream_id_1 = "lRwCZlDbxWLd2BDP-1D_8n___o0f4ZkEdA"
    stream_id_2 = "12lruitZ3cecVY1_SKgKB3___omJ6uHodA"

    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        message_service = bdk.messages()

        await message_service.send_message(
            stream_id_1, "<messageML>Hello, World!</messageML>"
        )

        with (
            open("/path/to/attachment1", "rb") as file1,
            open("/path/to/attachment2", "rb") as file2,
        ):
            message = Message(
                content="<messageML>Hello, World!</messageML>",
                attachments=[file1, file2],
            )
            await message_service.blast_message([stream_id_1, stream_id_2], message)

        with (
            open("/path/to/attachment", "rb") as attachment,
            open("/path/to/attachment-preview", "rb") as preview,
        ):
            message = Message(
                content="<messageML>Hello, World!</messageML>",
                attachments=[(attachment, preview)],
            )
            await message_service.blast_message([stream_id_1, stream_id_2], message)

        async for m in await message_service.search_all_messages(
            MessageSearchQuery(text="some_text", stream_id=stream_id_1)
        ):
            logging.debug(m.message_id)

        # import a message wih attachments
        content = "symphony"
        encoded_content = base64.b64encode(content.encode("ascii"))
        attachment = V4ImportedMessageAttachment(
            filename="text.txt", content=encoded_content.decode("ascii")
        )
        msg = V4ImportedMessage(
            intended_message_timestamp=1647353689268,
            intended_message_from_user_id=13056700580915,
            originating_system_id="fooChat",
            stream_id=stream_id_1,
            message="<messageML>This is an imported message!</messageML>",
            attachments=[attachment],
        )
        await message_service.import_messages([msg])

        logging.info("Obo example:")
        obo_auth_session = bdk.obo(username="username")
        async with bdk.obo_services(obo_auth_session) as obo_services:
            # Message ID can be retrieved by following guide here:
            # https://docs.developers.symphony.com/building-bots-on-symphony/datafeed/overview-of-streams
            await obo_services.messages().suppress_message("URL-Safe MessageID")
            obo_message = await obo_services.messages().send_message(stream_id_1, "Hello obo")
            await obo_services.messages().update_message(stream_id_1, obo_message.message_id, "Hello obo updated")

logging.config.fileConfig(
    Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False
)

asyncio.run(run())
