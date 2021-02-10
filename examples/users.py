import asyncio
import logging

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        user_service = bdk.users()
        details = await user_service.list_users_by_ids([12987981103610])
        logging.info(details)


logging.basicConfig(level=logging.DEBUG)
asyncio.run(run())
