from unittest.mock import patch, MagicMock, AsyncMock
import pytest

from symphony.bdk.core.auth.bot_authenticator import BotAuthenticatorRsa
from symphony.bdk.core.auth.exception import AuthUnauthorizedError
from symphony.bdk.core.config.model.bdk_bot_config import BdkBotConfig
from symphony.bdk.gen.api_client import ApiClient
from symphony.bdk.gen.configuration import Configuration
from symphony.bdk.gen.exceptions import ApiException
from symphony.bdk.gen.login_model.token import Token

from tests.core.config import minimal_retry_config
from tests.utils.resource_utils import get_resource_filepath


@pytest.fixture(name="mocked_api_client")
def fixture_mocked_api_client():
    def _create_api_client():  # We do this to have a new instance for each call
        api_client = MagicMock(ApiClient)
        api_client.call_api = AsyncMock()
        api_client.configuration = Configuration()
        return api_client

    return _create_api_client


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
async def test_bot_session_rsa(config, mocked_api_client):
    with patch("symphony.bdk.core.auth.bot_authenticator.create_signed_jwt", return_value="privateKey"):
        login_api_client = mocked_api_client()
        relay_api_client = mocked_api_client()

        login_api_client.call_api.return_value = Token(token="session_token")
        relay_api_client.call_api.return_value = Token(token="km_token")

        bot_authenticator = BotAuthenticatorRsa(config, login_api_client, relay_api_client, minimal_retry_config())
        session_token = await bot_authenticator.retrieve_session_token()
        km_token = await bot_authenticator.retrieve_key_manager_token()

        assert session_token == "session_token"
        assert km_token == "km_token"


@pytest.mark.asyncio
async def test_api_exception_rsa(config, mocked_api_client):
    with patch("symphony.bdk.core.auth.bot_authenticator.create_signed_jwt", return_value="privateKey"):
        login_api_client = mocked_api_client()
        relay_api_client = mocked_api_client()

        login_api_client.call_api.side_effect = ApiException(status=401)
        relay_api_client.call_api.side_effect = ApiException(status=401)

        bot_authenticator = BotAuthenticatorRsa(config, login_api_client, relay_api_client, minimal_retry_config())

        with pytest.raises(AuthUnauthorizedError):
            await bot_authenticator.retrieve_session_token()

        with pytest.raises(AuthUnauthorizedError):
            await bot_authenticator.retrieve_key_manager_token()
