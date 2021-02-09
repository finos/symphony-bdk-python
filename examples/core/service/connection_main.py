import asyncio

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.core.service.connection.model.connection_status import ConnectionStatus


class ConnectionMain:

    @staticmethod
    async def run():

        config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

        async with SymphonyBdk(config) as bdk:
            connection_service = bdk.connections()
            user_connection = await connection_service.list_connections(status=ConnectionStatus.ALL)
            print(user_connection)


if __name__ == "__main__":
    asyncio.run(ConnectionMain.run())
