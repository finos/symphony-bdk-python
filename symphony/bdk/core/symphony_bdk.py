from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.auth.authenticator_factory import AuthenticatorFactory
from symphony.bdk.core.auth.auth_session import AuthSession

from symphony.bdk.core.config.exception.bot_not_configured_exception import BotNotConfiguredException
from symphony.bdk.core.datafeed.datafeed_loop_v1 import DatafeedLoopV1
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi


class SymphonyBdk:
    """
    BDK entry point
    """

    def __init__(self, config):
        self._config = config
        self._api_client_factory = ApiClientFactory(config)

        self._authenticator_factory = AuthenticatorFactory(config, api_client_factory=self._api_client_factory)
        self._bot_session = None
        self._datafeed_loop = None

    async def bot_session(self) -> AuthSession:
        """
        Get the Bot authentication session. If the bot is not authenticated yet, perform the authentication for a new
        session.

        :return: The bot authentication session.
        """
        if self._bot_session is None:
            self._bot_session = await self._authenticator_factory.get_bot_authenticator().authenticate_bot()
        return self._bot_session

    def datafeed(self) -> DatafeedLoopV1:
        if self._datafeed_loop is None:
            self._datafeed_loop = self.get_datafeed_loop()
        return self._datafeed_loop

    def get_datafeed_loop(self) -> DatafeedLoopV1:
        if self._config.is_bot_configured():
            datafeed_agent_client = self._api_client_factory.get_agent_client()
            return DatafeedLoopV1(DatafeedApi(datafeed_agent_client), self._bot_session, self._config)
        else:
            raise BotNotConfiguredException

    async def close_clients(self):
        """
        Close all the existing api clients created by the api client factory.
        """
        await self._api_client_factory.close_clients()
