import asyncio

from symphony.bdk.core.config.bdk_config_loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


class MessageMain:

    @staticmethod
    async def run():
        stream_id_1 = "lRwCZlDbxWLd2BDP-1D_8n___o0f4ZkEdA"
        stream_id_2 = "12lruitZ3cecVY1_SKgKB3___omJ6uHodA"

        config_3 = BdkConfigLoader.load_from_symphony_dir("config.yaml")
        bdk = SymphonyBdk(config_3)
        try:
            message_service = await bdk.messages()
            with open("/path/to/attachment1", "rb") as file1, \
                    open("/path/to/attachment2", "rb") as file2:
                await message_service.blast_message(
                    [stream_id_1, stream_id_2],
                    "<messageML>Hello, World!</messageML>",
                    attachment=[file1, file2]
                )

        finally:
            await bdk.close_clients()


if __name__ == "__main__":
    asyncio.run(MessageMain.run())
