from unittest.mock import patch, MagicMock
from asyncmock import AsyncMock

import pytest

from symphony.bdk.core.auth.bot_authenticator import BotAuthenticatorRSA
from symphony.bdk.core.auth.exception.bdk_authentication_exception import AuthUnauthorizedException
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

        bot_authenticator = BotAuthenticatorRSA(config, login_api_client, relay_api_client)
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

        bot_authenticator = BotAuthenticatorRSA(config, login_api_client, relay_api_client)

        with pytest.raises(AuthUnauthorizedException):
            await bot_authenticator.retrieve_session_token()

        with pytest.raises(AuthUnauthorizedException):
            await bot_authenticator.retrieve_key_manager_token()


@pytest.mark.asyncio
async def test_authenticate_bot(config, mocked_api_client):
    with patch('symphony.bdk.core.auth.bot_authenticator.create_signed_jwt', return_value='privateKey'):
        login_api_client = mocked_api_client()
        relay_api_client = mocked_api_client()

        login_api_client.call_api.return_value = Token(token="session_token")
        relay_api_client.call_api.return_value = Token(token="km_token")

        bot_authenticator = BotAuthenticatorRSA(config, login_api_client, relay_api_client)
        auth_session = await bot_authenticator.authenticate_bot()

        assert await auth_session.session_token == "session_token"
        assert await auth_session.key_manager_token == "km_token"
