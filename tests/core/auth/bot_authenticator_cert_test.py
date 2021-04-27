from unittest.mock import MagicMock, AsyncMock
import pytest

from symphony.bdk.core.auth.bot_authenticator import BotAuthenticatorCert
from symphony.bdk.core.auth.exception import AuthUnauthorizedError
from symphony.bdk.core.config.model.bdk_bot_config import BdkBotConfig
from symphony.bdk.gen.api_client import ApiClient
from symphony.bdk.gen.configuration import Configuration
from symphony.bdk.gen.exceptions import ApiException
from symphony.bdk.gen.login_model.token import Token
from tests.core.config import minimal_retry_config


@pytest.fixture(name="mocked_api_client")
def fixture_mocked_api_client():
    def __loader():
        api_client = MagicMock(ApiClient)
        api_client.call_api = AsyncMock()
        api_client.configuration = Configuration()
        return api_client

    return __loader


@pytest.fixture(name="config")
def fixture_config():
    bot_config = {
        "username": "test_bot",
        "privateKey": {
            "path": "path/to/private_key"
        }
    }
    return BdkBotConfig(bot_config)


@pytest.mark.asyncio
async def test_bot_session_cert(mocked_api_client):
    session_auth_client = mocked_api_client()
    key_auth_client = mocked_api_client()

    session_auth_client.call_api.return_value = Token(token="session_token")
    key_auth_client.call_api.return_value = Token(token="km_token")

    bot_authenticator = BotAuthenticatorCert(session_auth_client, key_auth_client, minimal_retry_config())
    session_token = await bot_authenticator.retrieve_session_token()
    km_token = await bot_authenticator.retrieve_key_manager_token()

    assert session_token == "session_token"
    assert km_token == "km_token"


@pytest.mark.asyncio
async def test_api_exception_cert(mocked_api_client):
    session_auth_client = mocked_api_client()
    key_auth_client = mocked_api_client()

    session_auth_client.call_api.side_effect = ApiException(status=401)
    key_auth_client.call_api.side_effect = ApiException(status=401)

    bot_authenticator = BotAuthenticatorCert(session_auth_client, key_auth_client, minimal_retry_config())

    with pytest.raises(AuthUnauthorizedError):
        await bot_authenticator.retrieve_session_token()

    with pytest.raises(AuthUnauthorizedError):
        await bot_authenticator.retrieve_key_manager_token()


@pytest.mark.asyncio
async def test_authenticate_bot_cert(mocked_api_client):
    session_auth_client = mocked_api_client()
    key_auth_client = mocked_api_client()

    session_auth_client.call_api.return_value = Token(token="session_token")
    key_auth_client.call_api.return_value = Token(token="km_token")

    bot_authenticator = BotAuthenticatorCert(session_auth_client, key_auth_client, minimal_retry_config())
    auth_session = await bot_authenticator.authenticate_bot()

    assert await auth_session.session_token == "session_token"
    assert await auth_session.key_manager_token == "km_token"
