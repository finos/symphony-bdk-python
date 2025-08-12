import asyncio
import logging.config
from pathlib import Path

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    async with SymphonyBdk(config) as bdk:
        ext_app_authenticator = bdk.app_authenticator()

        app_auth = await ext_app_authenticator.authenticate_extension_app("appToken")
        ta = app_auth.app_token
        ts = app_auth.symphony_token
        # nosemgrep - please don't log secrets in production; this is just for demo purposes
        logging.debug("App token: %s, Symphony token: %s", ta, ts)
        # nosemgrep
        logging.debug(
            "Is token pair valid: %s", await ext_app_authenticator.is_token_pair_valid(ta, ts)
        )


logging.config.fileConfig(
    Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False
)

asyncio.run(run())
