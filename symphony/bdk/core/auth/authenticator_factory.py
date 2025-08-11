"""Module for instantiating various authenticator objects."""

from symphony.bdk.core.auth.bot_authenticator import (
    BotAuthenticator,
    BotAuthenticatorCert,
    BotAuthenticatorRsa,
)
from symphony.bdk.core.auth.exception import AuthInitializationError
from symphony.bdk.core.auth.ext_app_authenticator import (
    ExtensionAppAuthenticator,
    ExtensionAppAuthenticatorCert,
    ExtensionAppAuthenticatorRsa,
)
from symphony.bdk.core.auth.obo_authenticator import (
    OboAuthenticator,
    OboAuthenticatorCert,
    OboAuthenticatorRsa,
)
from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.gen.auth_api.certificate_authentication_api import (
    CertificateAuthenticationApi,
)
from symphony.bdk.gen.auth_api.certificate_pod_api import CertificatePodApi
from symphony.bdk.gen.login_api.authentication_api import AuthenticationApi
from symphony.bdk.gen.pod_api.pod_api import PodApi


class AuthenticatorFactory:
    """Authenticator Factory class

    Provides new instances for the main authenticators:
        - :class:`symphony.bdk.core.auth.bot_authenticator.BotAuthenticator`: to authenticate the main Bot service
          account
        - :class:`symphony.bdk.core.auth.obo_authenticator.OboAuthenticator`: to perform on-behalf-of authentication
        - :class:`symphony.bdk.core.auth.ext_app_authenticator.ExtensionAppAuthenticator`: to perform extension
          application authentication
    """

    def __init__(self, config: BdkConfig, api_client_factory: ApiClientFactory):
        """

        :param config: the bot configuration
        :param api_client_factory: the :class:`symphony.bdk.core.client.api_client_factory.ApiClientFactory` instance to
          create the BotAuthenticator from.
        """
        self._config = config
        self._api_client_factory = api_client_factory

    def get_bot_authenticator(self) -> BotAuthenticator:
        """Creates a new instance of a Bot Authenticator service.

        :return: a new :class:`symphony.bdk.core.auth.bot_authenticator.BotAuthenticator` instance.
        """
        if self._config.bot.is_rsa_configuration_valid():
            return BotAuthenticatorRsa(
                self._config.bot,
                self._api_client_factory.get_login_client(),
                self._api_client_factory.get_relay_client(),
                self._config.retry,
            )
        if self._config.bot.is_certificate_configuration_valid():
            return BotAuthenticatorCert(
                self._api_client_factory.get_session_auth_client(),
                self._api_client_factory.get_key_auth_client(),
                self._config.retry,
            )
        raise AuthInitializationError(
            "RSA or certificate authentication should be configured. "
            "Only one field among private key path or content should be configured "
            "for bot RSA authentication. "
            "The path field should be specified for bot certificate authentication."
        )

    def get_obo_authenticator(self) -> OboAuthenticator:
        """Creates a new instance of a Obo Authenticator service.

        :return: a new :class:`symphony.bdk.core.auth.obo_authenticator.OboAuthenticator` instance.
        """
        app_config = self._config.app
        if app_config.is_rsa_configuration_valid():
            return OboAuthenticatorRsa(
                app_config,
                AuthenticationApi(self._api_client_factory.get_login_client()),
                self._config.retry,
            )
        if app_config.is_certificate_configuration_valid():
            authentication_api = CertificateAuthenticationApi(
                self._api_client_factory.get_app_session_auth_client()
            )
            return OboAuthenticatorCert(authentication_api, self._config.retry)
        raise AuthInitializationError(
            "Application under 'app' field should be configured with a private key or "
            "a certificate in order to use OBO authentication."
        )

    def get_extension_app_authenticator(self) -> ExtensionAppAuthenticator:
        """Creates a new instance of an extension app authenticator service.

        :return: a new :class:`symphony.bdk.core.auth.ext_app_authenticator.ExtensionAppAuthenticator` instance.
        """
        app_config = self._config.app
        if app_config.is_rsa_configuration_valid():
            return ExtensionAppAuthenticatorRsa(
                AuthenticationApi(self._api_client_factory.get_login_client()),
                PodApi(self._api_client_factory.get_pod_client()),
                app_config.app_id,
                app_config.private_key,
                self._config.retry,
            )
        if app_config.is_certificate_configuration_valid():
            return ExtensionAppAuthenticatorCert(
                CertificateAuthenticationApi(
                    self._api_client_factory.get_app_session_auth_client()
                ),
                CertificatePodApi(
                    self._api_client_factory.get_app_session_auth_client()
                ),
                app_config.app_id,
                self._config.retry,
            )
        raise AuthInitializationError(
            "Application under 'app' field should be configured with a private key path or "
            "content in order to authenticate extension app."
        )
