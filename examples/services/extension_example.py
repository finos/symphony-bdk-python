import asyncio
import logging.config
from pathlib import Path

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.extension import BdkRetryConfigAware, retry_aware
from symphony.bdk.core.symphony_bdk import SymphonyBdk, register_extension


@register_extension
@retry_aware  # so that _retry_config attribute is set and @retry decorator can be used with the same retry config
class MyExtension(BdkRetryConfigAware):
    def __init__(self):
        self._bot_session = None
        self._config = None

    def set_auth_session(self, auth_session: AuthSession):
        logger.debug("Registering auth session")
        self._bot_session = auth_session

    def set_configuration(self, bdk_config: BdkConfig):
        logger.debug("Registering config: " + bdk_config.host)
        self._config = bdk_config

    def get_service(self):
        return self

    async def get_session_token(self):
        return await self._bot_session.session_token


async def run():
    async with SymphonyBdk(BdkConfigLoader.load_from_symphony_dir("config.yaml")) as bdk:
        service = bdk.extensions().get_service(MyExtension)
        logger.debug("Session token: " + await service.get_session_token())


logging.config.fileConfig(Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

asyncio.run(run())
