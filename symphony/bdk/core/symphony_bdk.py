from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.auth.authenticator_factory import AuthenticatorFactory
from symphony.bdk.core.auth.auth_session import AuthSession


class SymphonyBdk:
    """
    BDK entry point
    """

    def __init__(self, config):
        self._config = config
        self._api_client_factory = ApiClientFactory(config)

        self._authenticator_factory = AuthenticatorFactory(config, api_client_factory=self._api_client_factory)
        self._bot_session = None

    async def bot_session(self) -> AuthSession:
        """
        Get the Bot authentication session. If the bot is not authenticated yet, perform the authentication for a new
        session.

        :return: The bot authentication session.
        """
        if self._bot_session is None:
            self._bot_session = await self._authenticator_factory.get_bot_authenticator().authenticate_bot()
        return self._bot_session

    async def close_clients(self):
        """
        Close all the existing api clients created by the api client factory.
        """
        await self._api_client_factory.close_clients()
