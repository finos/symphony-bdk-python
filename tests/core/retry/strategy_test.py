import asyncio
from unittest.mock import Mock, AsyncMock

import pytest
from aiohttp import ClientConnectorError

import symphony.bdk.core.retry.strategy as strategy

from symphony.bdk.core.auth.exception import AuthUnauthorizedError
from symphony.bdk.core.retry import retry

from symphony.bdk.gen import ApiException
from tests.core.config import minimal_retry_config_with_attempts
from tests.core.retry import NoApiExceptionAfterCount, FixedChainedExceptions


class TestAuthenticationStrategy:
    """Testing authentication_retry strategy"""
    _retry_config = minimal_retry_config_with_attempts(1)

    @retry(retry=strategy.authentication_retry)
    async def _retryable_coroutine(self, thing):
        await asyncio.sleep(0.00001)
        return thing.go()

    @pytest.mark.asyncio
    async def test_unauthorized_is_raised(self):
        thing = NoApiExceptionAfterCount(2, status=401)
        with pytest.raises(AuthUnauthorizedError):
            await self._retryable_coroutine(thing)

        assert thing.call_count == 1

    @pytest.mark.asyncio
    async def test_unexpected_api_exception_is_raised(self):
        thing = NoApiExceptionAfterCount(2, status=404)
        with pytest.raises(ApiException):
            await self._retryable_coroutine(thing)

        assert thing.call_count == 1


class TestRefreshSessionStrategy:
    """Testing refresh_session_if_unauthorized strategy"""
    _retry_config = minimal_retry_config_with_attempts(2)

    @retry(retry=strategy.refresh_session_if_unauthorized)
    async def _retryable_coroutine(self, thing):
        await asyncio.sleep(0.00001)
        return thing.go()

    @pytest.mark.asyncio
    async def test_unauthorized_error_refreshes_session_and_tries_again(self):
        self._auth_session = Mock()
        self._auth_session.refresh = AsyncMock()
        thing = NoApiExceptionAfterCount(1, status=401)

        value = await self._retryable_coroutine(thing)

        self._auth_session.refresh.assert_called_once()
        assert value is True


class TestReadDatafeedStrategy:
    """Testing refresh_session_if_unauthorized strategy"""

    @retry(retry=strategy.read_datafeed_retry)
    async def _retryable_coroutine(self, thing):
        await asyncio.sleep(0.00001)
        return thing.go()

    @pytest.mark.asyncio
    async def test_client_error_recreates_datafeed_and_and_tries_again(self):
        self._retry_config = minimal_retry_config_with_attempts(2)
        self._auth_session = Mock()
        self.recreate_datafeed = AsyncMock()
        thing = NoApiExceptionAfterCount(1, status=400)

        value = await self._retryable_coroutine(thing)

        self.recreate_datafeed.assert_called_once()
        assert value is True

    @pytest.mark.asyncio
    async def test_unauthorized_error_refreshes_session_and_and_tries_again(self):
        self._retry_config = minimal_retry_config_with_attempts(2)
        self._auth_session = Mock()
        self._auth_session.refresh = AsyncMock()
        thing = NoApiExceptionAfterCount(1, status=401)

        value = await self._retryable_coroutine(thing)

        self._auth_session.refresh.assert_called_once()
        assert value is True

    @pytest.mark.asyncio
    async def test_unexpected_api_exception_is_raised(self):
        self._retry_config = minimal_retry_config_with_attempts(1)
        thing = NoApiExceptionAfterCount(2, status=404)
        with pytest.raises(ApiException):
            await self._retryable_coroutine(thing)

        assert thing.call_count == 1


@pytest.mark.asyncio
async def test_should_retry():
    strategies = [TestAuthenticationStrategy(), TestRefreshSessionStrategy(), TestReadDatafeedStrategy()]
    connection_key = Mock()
    connection_key.ssl = "ssl"
    exception_from_a_timeout = ClientConnectorError(connection_key, TimeoutError())
    exception_from_a_timeout.__cause__ = TimeoutError()
    thing = FixedChainedExceptions([ApiException(429), ApiException(500), exception_from_a_timeout])

    for s in strategies:
        s._retry_config = minimal_retry_config_with_attempts(4)

        value = await s._retryable_coroutine(thing)

        assert value is True
        assert thing.call_count == 4
        thing.reset()  # Reset the counters
