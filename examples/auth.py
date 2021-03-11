import asyncio
import logging.config

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


logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(trace_id)s - %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False
        }
    }
})

asyncio.run(run())
