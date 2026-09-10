from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from symphony.bdk.core.auth.bot_authenticator import BotAuthenticatorCert
from symphony.bdk.core.auth.exception import AuthUnauthorizedError
from symphony.bdk.gen.api_client import ApiClient
from symphony.bdk.gen.configuration import Configuration
from symphony.bdk.gen.exceptions import ApiException
from symphony.bdk.gen.login_model.token import Token
from tests.core.config import minimal_retry_config


@pytest.fixture(name="mocked_api_client")
def fixture_mocked_api_client():
    def _create_api_client():  # We do this to have a new instance for each call
        api_client = MagicMock(ApiClient)
        api_client.configuration = Configuration()
        return api_client

    return _create_api_client


@pytest.mark.asyncio
async def test_bot_session_cert(mocked_api_client):
    with patch("symphony.bdk.core.auth.bot_authenticator.CertificateAuthenticationApi") as cert_auth_api_class_mock:
        session_auth_client = mocked_api_client()
        key_auth_client = mocked_api_client()

        cert_auth_api_instance_mock = MagicMock()
        cert_auth_api_instance_mock.v1_authenticate_post = AsyncMock()
        cert_auth_api_instance_mock.v1_authenticate_post.side_effect = [
            Token(token="session_token"),
            Token(token="km_token"),
        ]
        cert_auth_api_class_mock.return_value = cert_auth_api_instance_mock

        bot_authenticator = BotAuthenticatorCert(
            session_auth_client, key_auth_client, minimal_retry_config()
        )
        session_token = await bot_authenticator.retrieve_session_token()
        km_token = await bot_authenticator.retrieve_key_manager_token()

        assert session_token == "session_token"
        assert km_token == "km_token"


@pytest.mark.asyncio
async def test_api_exception_cert(mocked_api_client):
    with patch("symphony.bdk.core.auth.bot_authenticator.CertificateAuthenticationApi") as cert_auth_api_class_mock:
        session_auth_client = mocked_api_client()
        key_auth_client = mocked_api_client()

        cert_auth_api_instance_mock = MagicMock()
        cert_auth_api_instance_mock.v1_authenticate_post = AsyncMock(side_effect=ApiException(status=401))
        cert_auth_api_class_mock.return_value = cert_auth_api_instance_mock

        bot_authenticator = BotAuthenticatorCert(
            session_auth_client, key_auth_client, minimal_retry_config()
        )

        with pytest.raises(AuthUnauthorizedError):
            await bot_authenticator.retrieve_session_token()

        with pytest.raises(AuthUnauthorizedError):
            await bot_authenticator.retrieve_key_manager_token()
