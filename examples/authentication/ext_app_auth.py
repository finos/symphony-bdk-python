import asyncio
import logging.config
import os
from pathlib import Path

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    async with SymphonyBdk(config) as bdk:
        ext_app_authenticator = bdk.app_authenticator()

        app_auth = await ext_app_authenticator.authenticate_extension_app("appToken")
        ta = app_auth.app_token
        ts = app_auth.symphony_token
        logging.debug("App token: %s, Symphony token: %s", ta, ts)

        logging.debug("Is token pair valid: %s", await ext_app_authenticator.is_token_pair_valid(ta, ts))

config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
logging.config.fileConfig(Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False)

if os.name == "nt" and config.proxy is not None:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(run())
