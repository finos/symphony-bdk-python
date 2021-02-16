from symphony.bdk.core.auth.bot_authenticator import BotAuthenticator, BotAuthenticatorRsa
from symphony.bdk.core.auth.exception import AuthInitializationError
from symphony.bdk.core.auth.obo_authenticator import OboAuthenticator, OboAuthenticatorRsa
from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.config.model.bdk_config import BdkConfig


class AuthenticatorFactory:
    """Authenticator Factory class

    Provides new instances for the main authenticators :

        - Bot Authenticator   : to authenticate the main Bot service account
        - OboAuthenticator    : to perform on-behalf-of authentication
    """

    def __init__(self, config: BdkConfig, api_client_factory: ApiClientFactory):
        """

        :param config: the bot configuration
        :param api_client_factory: the ApiClientFactory instance to create the BotAuthenticator from.
        """
        self._config = config
        self._api_client_factory = api_client_factory

    def get_bot_authenticator(self) -> BotAuthenticator:
        """Creates a new instance of a Bot Authenticator service.

        :return: a new BotAuthenticator instance.
        """
        if self._config.bot.is_rsa_configuration_valid():
            return BotAuthenticatorRsa(
                bot_config=self._config.bot,
                login_api_client=self._api_client_factory.get_login_client(),
                relay_api_client=self._api_client_factory.get_relay_client()
            )
        raise AuthInitializationError("RSA authentication should be configured. Only one field among private key "
                                          "path or content should be configured for bot authentication.")

    def get_obo_authenticator(self) -> OboAuthenticator:
        """Creates a new instance of a Obo Authenticator service.

        :return: a new OboAuthenticator instance.
        """
        if self._config.app.is_rsa_authentication_configured() and self._config.app.is_rsa_configuration_valid():
            return OboAuthenticatorRsa(
                app_config=self._config.app,
                login_api_client=self._api_client_factory.get_login_client()
            )
        raise AuthInitializationError("Only one of private key path or content should be configured for "
                                          "extension app authentication.")
