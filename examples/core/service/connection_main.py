import asyncio

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


class ConnectionMain:

    @staticmethod
    async def run():

        config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

        async with SymphonyBdk(config) as bdk:
            connection_service = bdk.connections()
            user_connection = await connection_service.get_connection(13056700579873)
            print(user_connection)


if __name__ == "__main__":
    asyncio.run(ConnectionMain.run())
