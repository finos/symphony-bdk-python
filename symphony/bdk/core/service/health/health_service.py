from symphony.bdk.gen.agent_api.system_api import SystemApi
from symphony.bdk.gen.agent_api.signals_api import SignalsApi
from symphony.bdk.gen.agent_model.agent_info import AgentInfo

from symphony.bdk.gen.agent_model.v3_health import V3Health


class HealthService:
    """Service class for checking health of the Agent server."""

    def __init__(self, system_api: SystemApi, signals_api: SignalsApi):
        self._system_api = system_api
        self._signals_api = signals_api

    async def health_check(self) -> V3Health:
        """ Returns the connectivity status of your Agent server.
        Wraps the `Health Check v3 <https://developers.symphony.com/restapi/reference#health-check-v3>`_ endpoint.
        If your Agent server is started and running properly, the status value will be UP.
        Available on Agent 2.57.0 and above.

        :return: V3Health: the connectivity status of your Agent server.
        """
        return await self._system_api.v3_health()

    async def health_check_extended(self) -> V3Health:
        """Returns the connectivity status of the Agent services as well as users connectivity.
        Wraps the `Healt Check Extended v3 <https://developers.symphony.com/restapi/reference#health-check-extended-v3>`_ endpoint.
        Available on Agent 2.57.0 and above.

        :return: V3Health: the connectivity status of the Agent services as well as users connectivity.
        """
        return await self._system_api.v3_extended_health()

    async def get_agent_info(self) -> AgentInfo:
        """Gets information about the Agent.
        Wraps the `Agent Info v1 <https://developers.symphony.com/restapi/reference#agent-info-v1>`_ endpoint.
        Available on Agent 2.53.0 and above.

        :return: AgentInfo: information of  the agent server.
        """
        return await self._signals_api.v1_info_get()
