import asyncio
import logging.config
import os

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("/Users/reed.feldman/devx/test-bot-python/resources/config.yaml")
    async with SymphonyBdk(config) as bdk:
        logging.info("Obo example:")
        obo_auth_session = bdk.obo(username="admin@symphony.com")
        async with bdk.obo_services(obo_auth_session) as obo_services:
            await obo_services.messages().suppress_message("Kl3ysGcU0MUPdGsHQl_DgH___oc2v3k1bQ")


logging.basicConfig(level=logging.DEBUG)

asyncio.run(run())