import asyncio
import logging

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    async with SymphonyBdk(config) as bdk:
        auth_session = bdk.bot_session()
        logging.info(await auth_session.key_manager_token)
        logging.info(await auth_session.session_token)
        logging.info("Obo example:")
        obo_auth_session = bdk.obo(username="username")
        logging.info(await obo_auth_session.session_token)

    # update private key
    config.setBotConfig(privateKey="/path/to/new_private_key")

    # update certificate
    config.setBotConfig(certificate="/path/to/new_certificate")

   # update both private key and certificate
    config.setBotConfig("/path/to/new_private_key", "/path/to/new_certificate")
    async with SymphonyBdk(config) as bdk:
        auth_session = bdk.bot_session()
        logging.info(await auth_session.key_manager_token)
        logging.info(await auth_session.session_token)

logging.basicConfig(level=logging.DEBUG)
asyncio.run(run())
