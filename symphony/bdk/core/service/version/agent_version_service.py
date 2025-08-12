import re
from datetime import datetime, timezone

from symphony.bdk.core.auth.jwt_helper import generate_expiration_time
from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig
from symphony.bdk.core.retry import retry
from symphony.bdk.gen.agent_api.signals_api import SignalsApi
from symphony.bdk.gen.exceptions import ApiException

MIN_MAJOR_VERSION = 24
MIN_MINOR_VERSION = 12
VERSION_REGEXP = r"Agent-(\d+)\.(\d+)\..*"


class AgentVersionService:
    """Service class has one purpose only. It checks if version of agents supports simplified key delivery mechanism"""

    def __init__(self, signals_api: SignalsApi, retry_config: BdkRetryConfig):
        self._signals_api = signals_api
        self._retry_config = retry_config
        self._is_skd_supported = None
        self._expire_at = -1

    async def is_skd_supported(self) -> bool:
        """AgentVersionService stores cached version  flag.
        Caching interval is the same as in to session token caching.
        Once cache is expired it calls agent info api to update version.

        :return: boolean flag if skd supported for agent
        """
        if (
            self._is_skd_supported is not None
            and self._expire_at > datetime.now(timezone.utc).timestamp()
        ):
            return self._is_skd_supported
        self._expire_at = generate_expiration_time()
        self._is_skd_supported = await self._get_agent_skd_support()
        return self._is_skd_supported

    @retry
    async def _get_agent_skd_support(self) -> bool:
        try:
            agent_info = await self._signals_api.v1_info_get()
            if not agent_info or not agent_info.version:
                return False
        except ApiException:
            return False
        agent_major_version, agent_minor_version = self._parse_version(agent_info.version)
        if not agent_major_version:
            return False
        if agent_major_version == MIN_MAJOR_VERSION:
            return agent_minor_version >= MIN_MINOR_VERSION
        return agent_major_version > MIN_MAJOR_VERSION

    @staticmethod
    def _parse_version(version_string):
        if not version_string:
            return None, None
        match = re.match(VERSION_REGEXP, version_string)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None, None
