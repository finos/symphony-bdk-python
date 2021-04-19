import asyncio
import logging
from pathlib import Path

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    stream_id_1 = "lRwCZlDbxWLd2BDP-1D_8n___o0f4ZkEdA"
    stream_id_2 = "12lruitZ3cecVY1_SKgKB3___omJ6uHodA"

    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        message_service = bdk.messages()

        await message_service.send_message(stream_id_1, "<messageML>Hello, World!</messageML>")

        with open("/path/to/attachment1", "rb") as file1, \
                open("/path/to/attachment2", "rb") as file2:
            await message_service.blast_message(
                [stream_id_1, stream_id_2],
                "<messageML>Hello, World!</messageML>",
                attachment=[file1, file2]
            )


logging.config.fileConfig(Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False)

asyncio.run(run())
