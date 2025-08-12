import asyncio
import logging.config
from pathlib import Path

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.connection.model.connection_status import ConnectionStatus
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        connection_service = bdk.connections()
        user_connection = await connection_service.list_connections(status=ConnectionStatus.ALL)
        logging.info(user_connection)


logging.config.fileConfig(
    Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False
)

asyncio.run(run())
