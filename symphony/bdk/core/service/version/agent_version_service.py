import re

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig
from symphony.bdk.core.retry import retry
from symphony.bdk.gen.agent_api.signals_api import SignalsApi
from symphony.bdk.gen.exceptions import ApiException

MIN_MAJOR_VERSION = 24
MIN_MINOR_VERSION = 12
VERSION_REGEXP = r"Agent-(\d+)\.(\d+)\..*"


class AgentVersionService:
    """Service class has one purpose only. It checks if version of agents supports simplified key delivery mechanism

    """

    def __init__(self, signals_api: SignalsApi, auth_session: AuthSession, retry_config: BdkRetryConfig):
        self._signals_api = signals_api
        self._retry_config = retry_config

    @retry
    async def is_skd_supported(self) -> bool:
        """
        :return: boolean flag if skd supported for agent
        """
        try:
            agent_info = await self._signals_api.v1_info_get()
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
        match = re.match(r"Agent-(\d+)\.(\d+)\..*", version_string)
        if match:
            return int(match.group(1)), int(match.group(2))

        return None, None
