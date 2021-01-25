from symphony.bdk.core.auth.exception.bdk_authentication_exception import AuthInitializationException
from symphony.bdk.core.auth.bot_authenticator import BotAuthenticator, BotAuthenticatorRSA
from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.config.model.bdk_config import BdkConfig


class AuthenticatorFactory:
    """Authenticator Factory class

    Provides new instances for the main authenticators :

        - Bot Authenticator   : to authenticate the main Bot service account
        - OboAuthenticator    : to perform on-behalf-of authentication
    """

    def __init__(self, config: BdkConfig, api_client_factory: ApiClientFactory):
        self._config = config
        self._api_client_factory = api_client_factory

    def get_bot_authenticator(self) -> BotAuthenticator:
        """Creates a new instance of a Bot Authenticator service.

        :return: a new BotAuthenticator instance.

        """
        if self._config.bot.is_rsa_authentication_configured():
            if not self._config.bot.is_rsa_configuration_valid():
                raise AuthInitializationException("Only one of private key path or content should be configured for "
                                                  "bot authentication.")
            return BotAuthenticatorRSA(
                bot_config=self._config.bot,
                login_api_client=self._api_client_factory.get_login_client(),
                relay_api_client=self._api_client_factory.get_relay_client()
            )
