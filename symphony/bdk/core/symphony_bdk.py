from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.auth.authenticator_factory import AuthenticatorFactory


class SymphonyBdk:
    """
    BDK entry point
    """

    def __init__(self, config):
        self.__config = config
        self.__api_client_factory = ApiClientFactory(config)

        self.__authenticator_factory = AuthenticatorFactory(config, api_client_factory=self.__api_client_factory)
        self.__bot_session = None

    async def bot_session(self):
        """
        Get the Bot authentication session. If the bot is not authenticated yet, perform the authentication for a new
        session.

        Returns: The bot authentication session.

        """
        if self.__bot_session is None:
            self.__bot_session = await self.__authenticator_factory.get_bot_authenticator().authenticate_bot()
        return self.__bot_session
