from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from symphony.bdk.core.auth.exception import AuthUnauthorizedError
from symphony.bdk.core.auth.obo_authenticator import OboAuthenticatorRsa
from symphony.bdk.core.config.model.bdk_app_config import BdkAppConfig
from symphony.bdk.gen.api_client import ApiClient, Configuration
from symphony.bdk.gen.exceptions import ApiException
from symphony.bdk.gen.login_model.token import Token


@pytest.fixture(name="config")
def fixture_config():
    app_config = {
        "appId": "test_bot",
        "privateKey": {
            "path": "path/to/private_key"
        }
    }
    return BdkAppConfig(app_config)


@pytest.fixture(name="api_client")
def fixture_api_client():
    api_client = MagicMock(ApiClient)
    api_client.call_api = AsyncMock()
    api_client.configuration = Configuration()
    return api_client


@pytest.mark.asyncio
async def test_obo_session_username(config, api_client):
    with patch("symphony.bdk.core.auth.obo_authenticator.create_signed_jwt", return_value="privateKey"):
        api_client.call_api.return_value = Token(token="session_token")

        obo_authenticator = OboAuthenticatorRsa(config, api_client)
        session_token = await obo_authenticator.retrieve_obo_session_token_by_username("username")

        assert session_token == "session_token"


@pytest.mark.asyncio
async def test_obo_session_user_id(config, api_client):
    with patch("symphony.bdk.core.auth.obo_authenticator.create_signed_jwt", return_value="privateKey"):
        api_client.call_api.return_value = Token(token="session_token")

        obo_authenticator = OboAuthenticatorRsa(config, api_client)
        session_token = await obo_authenticator.retrieve_obo_session_token_by_user_id(1234)

        assert session_token == "session_token"


@pytest.mark.asyncio
async def test_api_exception(config, api_client):
    with patch("symphony.bdk.core.auth.obo_authenticator.create_signed_jwt", return_value="privateKey"):
        api_client.call_api.side_effect = ApiException()

        obo_authenticator = OboAuthenticatorRsa(config, api_client)

        with pytest.raises(AuthUnauthorizedError):
            await obo_authenticator.retrieve_obo_session_token_by_username("username")

        with pytest.raises(AuthUnauthorizedError):
            await obo_authenticator.retrieve_obo_session_token_by_user_id(1234)


@pytest.mark.asyncio
async def test_authenticate_by_username(config, api_client):
    with patch("symphony.bdk.core.auth.obo_authenticator.create_signed_jwt", return_value="privateKey"):
        api_client.call_api.return_value = Token(token="session_token")

        obo_authenticator = OboAuthenticatorRsa(config, api_client)
        obo_session = obo_authenticator.authenticate_by_username("username")

        assert await obo_session.session_token == "session_token"


@pytest.mark.asyncio
async def test_authenticate_by_user_id(config, api_client):
    with patch("symphony.bdk.core.auth.obo_authenticator.create_signed_jwt", return_value="privateKey"):
        api_client.call_api.return_value = Token(token="session_token")

        obo_authenticator = OboAuthenticatorRsa(config, api_client)
        obo_session = obo_authenticator.authenticate_by_user_id(1234)

        assert await obo_session.session_token == "session_token"
