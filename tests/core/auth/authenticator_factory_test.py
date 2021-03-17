from unittest.mock import MagicMock, Mock

import pytest

from symphony.bdk.core.auth.authenticator_factory import AuthenticatorFactory
from symphony.bdk.core.auth.exception import AuthInitializationError
from symphony.bdk.core.auth.ext_app_authenticator import ExtensionAppAuthenticatorRsa
from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.config.model.bdk_authentication_config import BdkAuthenticationConfig
from tests.utils.resource_utils import get_config_resource_filepath


@pytest.fixture(name="config")
def fixture_config():
    return BdkConfigLoader.load_from_file(get_config_resource_filepath("config.yaml"))


@pytest.fixture(name="api_client_factory")
def fixture_api_client_factory():
    factory = MagicMock(ApiClientFactory)
    factory.get_login_client.return_value = Mock()
    factory.get_relay_client.return_value = Mock()
    return factory


def test_get_bot_authenticator(config, api_client_factory):
    authenticator_factory = AuthenticatorFactory(config, api_client_factory)
    assert authenticator_factory.get_bot_authenticator() is not None


def test_get_bot_authenticator_failed(config, api_client_factory):
    bot_config = MagicMock()
    bot_config.is_rsa_authentication_configured.return_value = True
    bot_config.is_rsa_configuration_valid.return_value = False
    config.bot = bot_config
    authenticator_factory = AuthenticatorFactory(config, api_client_factory)
    with pytest.raises(AuthInitializationError):
        authenticator_factory.get_bot_authenticator()


def test_get_obo_authenticator(config, api_client_factory):
    authenticator_factory = AuthenticatorFactory(config, api_client_factory)
    assert authenticator_factory.get_obo_authenticator() is not None


def test_get_obo_authenticator_failed(config, api_client_factory):
    app_config = MagicMock()
    app_config.is_rsa_configuration_valid.return_value = False
    config.app = app_config
    authenticator_factory = AuthenticatorFactory(config, api_client_factory)
    with pytest.raises(AuthInitializationError):
        authenticator_factory.get_obo_authenticator()


def test_get_ext_app_authenticator_no_app_configured(config, api_client_factory):
    config.app = BdkAuthenticationConfig()  # remove the app configuration
    authenticator_factory = AuthenticatorFactory(config, api_client_factory)

    with pytest.raises(AuthInitializationError):
        authenticator_factory.get_extension_app_authenticator()


def test_get_ext_app_authenticator_app_wrongly_configured(config, api_client_factory):
    app_config = MagicMock()
    app_config.is_rsa_configuration_valid.return_value = False
    config.app = app_config

    authenticator_factory = AuthenticatorFactory(config, api_client_factory)

    with pytest.raises(AuthInitializationError):
        authenticator_factory.get_extension_app_authenticator()


def test_get_ext_app_authenticator_app(config, api_client_factory):
    authenticator_factory = AuthenticatorFactory(config, api_client_factory)
    extension_app_authenticator = authenticator_factory.get_extension_app_authenticator()

    assert extension_app_authenticator is not None
    assert isinstance(extension_app_authenticator, ExtensionAppAuthenticatorRsa)
