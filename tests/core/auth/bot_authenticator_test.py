from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from symphony.bdk.core.auth.bot_authenticator import BotAuthenticatorRsa
from symphony.bdk.core.auth.exception import AuthUnauthorizedError
from symphony.bdk.core.config.model.bdk_config import *
from symphony.bdk.gen.api_client import ApiClient
from symphony.bdk.gen.configuration import Configuration
from symphony.bdk.gen.exceptions import ApiException
from symphony.bdk.gen.login_model.token import Token

@pytest.fixture()
def config():
    bot_config = {
        "username": "test_bot",
        "privateKey": {
            "path": "path/to/private_key"
        }
    }
    return BdkBotConfig(bot_config)

@pytest.fixture()
def bdk_config(config):
    bdk_config = BdkConfig()
    bdk_config.bot = config
    return bdk_config

@pytest.fixture()
def mocked_api_client():
    def __loader():
        api_client = MagicMock(ApiClient)
        api_client.call_api = AsyncMock()
        api_client.configuration = Configuration()
        return api_client

    return __loader

@pytest.mark.asyncio
async def test_bot_session(config, mocked_api_client):
    with patch('symphony.bdk.core.auth.bot_authenticator.create_signed_jwt', return_value='privateKey'):
        login_api_client = mocked_api_client()
        relay_api_client = mocked_api_client()

        login_api_client.call_api.return_value = Token(token="session_token")
        relay_api_client.call_api.return_value = Token(token="km_token")

        bot_authenticator = BotAuthenticatorRsa(config, login_api_client, relay_api_client)
        session_token = await bot_authenticator.retrieve_session_token()
        km_token = await bot_authenticator.retrieve_key_manager_token()

        assert session_token == "session_token"
        assert km_token == "km_token"


@pytest.mark.asyncio
async def test_api_exception(config, mocked_api_client):
    with patch('symphony.bdk.core.auth.bot_authenticator.create_signed_jwt', return_value='privateKey'):
        login_api_client = mocked_api_client()
        relay_api_client = mocked_api_client()

        login_api_client.call_api.side_effect = ApiException()
        relay_api_client.call_api.side_effect = ApiException()

        bot_authenticator = BotAuthenticatorRsa(config, login_api_client, relay_api_client)

        with pytest.raises(AuthUnauthorizedError):
            await bot_authenticator.retrieve_session_token()

        with pytest.raises(AuthUnauthorizedError):
            await bot_authenticator.retrieve_key_manager_token()


@pytest.mark.asyncio
async def test_authenticate_bot(config, mocked_api_client):
    with patch('symphony.bdk.core.auth.bot_authenticator.create_signed_jwt', return_value='privateKey'):
        login_api_client = mocked_api_client()
        relay_api_client = mocked_api_client()

        login_api_client.call_api.return_value = Token(token="session_token")
        relay_api_client.call_api.return_value = Token(token="km_token")

        bot_authenticator = BotAuthenticatorRsa(config, login_api_client, relay_api_client)
        auth_session = await bot_authenticator.authenticate_bot()

        assert await auth_session.session_token == "session_token"
        assert await auth_session.key_manager_token == "km_token"

@pytest.mark.asyncio
async def test_authenticate_with_private_key_content(bdk_config, mocked_api_client):
    with patch('symphony.bdk.core.auth.bot_authenticator.create_signed_jwt', return_value='privateKey'):
        login_api_client = mocked_api_client()
        relay_api_client = mocked_api_client()

        login_api_client.call_api.return_value = Token(token="session_token")
        relay_api_client.call_api.return_value = Token(token="km_token")

        private_key_string = '-----BEGIN RSA PRIVATE KEY-----\n'\
                             '1Tgj93dkNzk7HwjdpxDDn2wQgaRA6lDAQ+NMYZ2i81J8lhC5toRHtSzLp5Ku+IKL\n'\
                             '-----END RSA PRIVATE KEY-----'
        bdk_config.bot.private_key.setContent(rsa_key_content=private_key_string)

        bot_authenticator = BotAuthenticatorRsa(bdk_config.bot, login_api_client, relay_api_client)
        auth_session = await bot_authenticator.authenticate_bot()

        assert bdk_config.bot.private_key.path is None
        assert bdk_config.bot.private_key.content == private_key_string
        assert await auth_session.session_token == "session_token"
        assert await auth_session.key_manager_token == "km_token"

@pytest.mark.asyncio
async def test_authenticate_with_certificate_content(bdk_config, mocked_api_client):
    with patch('symphony.bdk.core.auth.bot_authenticator.create_signed_jwt', return_value='privateKey'):
        login_api_client = mocked_api_client()
        relay_api_client = mocked_api_client()

        login_api_client.call_api.return_value = Token(token="session_token")
        relay_api_client.call_api.return_value = Token(token="km_token")

        certificate_string = '-----BEGIN CERTIFICATE-----\n'\
                             'ggEBAL5Z8cEbWs5jnXxWneP1nO9Hu6oCWErdK4aPDb/otarsMF0ZYmWKR3Urr1Fe\n'\
                             '-----END CERTIFICATE-----'
        bdk_config.bot.certificate.setContent(certificate_content=certificate_string)

        bot_authenticator = BotAuthenticatorRsa(bdk_config.bot, login_api_client, relay_api_client)
        auth_session = await bot_authenticator.authenticate_bot()

        assert bdk_config.bot.certificate.path is None
        assert bdk_config.bot.certificate.content == certificate_string
        assert await auth_session.session_token == "session_token"
        assert await auth_session.key_manager_token == "km_token"
