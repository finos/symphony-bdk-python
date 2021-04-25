from unittest.mock import MagicMock, AsyncMock, Mock
import pytest

from symphony.bdk.core.auth.bot_authenticator import BotAuthenticator
from symphony.bdk.core.auth.exception import AuthUnauthorizedError
from symphony.bdk.gen import ApiClient, ApiException
from tests.core.config import minimal_retry_config_with_attempts


class DummyBotAuthenticator(BotAuthenticator):

    async def _authenticate_and_get_token(self, api_client: ApiClient) -> str:
        pass


@pytest.mark.asyncio
async def test_success():
    api_client = Mock()
    bot_authenticator = DummyBotAuthenticator(api_client, api_client, minimal_retry_config_with_attempts(1))
    bot_authenticator._authenticate_and_get_token = AsyncMock()
    bot_authenticator._authenticate_and_get_token.return_value = "1234"

    value = await bot_authenticator._try_authenticate_and_get_token(api_client)

    assert value == "1234"
    bot_authenticator._authenticate_and_get_token.assert_called_once()


@pytest.mark.asyncio
async def test_unauthorized():
    api_client = MagicMock(ApiClient)
    bot_authenticator = DummyBotAuthenticator(api_client, api_client, minimal_retry_config_with_attempts(1))
    bot_authenticator._authenticate_and_get_token = AsyncMock()
    bot_authenticator._authenticate_and_get_token.side_effect = ApiException(401)

    with pytest.raises(AuthUnauthorizedError):
        await bot_authenticator._try_authenticate_and_get_token(api_client)

    bot_authenticator._authenticate_and_get_token.assert_called_once()


@pytest.mark.asyncio
async def test_unexpected_api_exception():
    api_client = MagicMock(ApiClient)
    bot_authenticator = DummyBotAuthenticator(api_client, api_client, minimal_retry_config_with_attempts(1))
    bot_authenticator._authenticate_and_get_token = AsyncMock()
    bot_authenticator._authenticate_and_get_token.side_effect = ApiException(404)

    with pytest.raises(ApiException):
        await bot_authenticator._try_authenticate_and_get_token(api_client)

    bot_authenticator._authenticate_and_get_token.assert_called_once()


@pytest.mark.asyncio
async def test_should_retry():
    api_client = MagicMock(ApiClient)
    bot_authenticator = DummyBotAuthenticator(api_client, api_client, minimal_retry_config_with_attempts(4))
    bot_authenticator._authenticate_and_get_token = AsyncMock()
    exception_from_a_timeout = Exception()
    exception_from_a_timeout.__cause__ = TimeoutError()
    bot_authenticator._authenticate_and_get_token.side_effect = [ApiException(429),
                                                                 ApiException(500),
                                                                 exception_from_a_timeout,
                                                                 "1234"]

    value = await bot_authenticator._try_authenticate_and_get_token(api_client)

    assert value == "1234"
    assert bot_authenticator._authenticate_and_get_token.call_count == 4

@pytest.mark.asyncio
async def test_retries_exhausted():
    api_client = MagicMock(ApiClient)
    bot_authenticator = DummyBotAuthenticator(api_client, api_client, minimal_retry_config_with_attempts(3))
    bot_authenticator._authenticate_and_get_token = AsyncMock()
    bot_authenticator._authenticate_and_get_token.side_effect = ApiException(429)

    with pytest.raises(ApiException):
        await bot_authenticator._try_authenticate_and_get_token(api_client)

    assert bot_authenticator._authenticate_and_get_token.call_count == 3
