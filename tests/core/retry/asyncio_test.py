import asyncio

import pytest
import tenacity

from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig
from symphony.bdk.core.retry import retry
from symphony.bdk.gen import ApiException


class NoApiExceptionAfterCount(object):
    """Holds counter state for invoking a method several times in a row."""

    def __init__(self, count, status=400):
        self.counter = 0
        self.count = count
        self.status = status

    def go(self):
        """Raise an ApiException until after count threshold has been crossed.

        Then return True.
        """
        if self.counter < self.count:
            self.counter += 1
            raise ApiException(status=self.status, reason="Hi there, I'm an ApiException")
        return True


class NoIOErrorAfterCount(object):
    """Holds counter state for invoking a method several times in a row."""

    def __init__(self, count):
        self.counter = 0
        self.count = count

    def go(self):
        """Raise an IOError until after count threshold has been crossed.

        Then return True.
        """
        if self.counter < self.count:
            self.counter += 1
            raise IOError("Hi there, I'm an IOError")
        return True


def minimal_retry_config_with_attempts(max_attempts: int):
    retry_config = BdkRetryConfig()
    retry_config.multiplier = 1
    retry_config.initial_interval = 10
    retry_config.max_interval = 10
    retry_config.max_attempts = max_attempts
    return retry_config


@retry
async def _retryable_coroutine(thing):
    await asyncio.sleep(0.00001)
    return thing.go()


@retry(retry=tenacity.retry_if_result(lambda x: False))
async def _non_retryable_coroutine(thing):
    return thing.go()


@retry(stop=tenacity.stop_after_attempt(2))
async def _retryable_coroutine_with_2_attempts(thing):
    await asyncio.sleep(0.00001)
    thing.go()


@pytest.mark.asyncio
async def test_retry():
    thing = NoIOErrorAfterCount(5)
    value = await _retryable_coroutine(thing)
    assert thing.counter == thing.count
    assert value is True


@pytest.mark.asyncio
async def test_stop_after_attempt():
    thing = NoIOErrorAfterCount(2)
    try:
        await _retryable_coroutine_with_2_attempts(thing)
    except tenacity.RetryError:
        assert thing.counter == 2
    assert thing.counter == 2


@pytest.mark.asyncio
async def test_with_no_retry_should_raise_exception():
    thing = NoApiExceptionAfterCount(2)

    with pytest.raises(ApiException):
        await _non_retryable_coroutine(thing)

    assert thing.counter == 1


class TestDecoratorWrapper:
    """Testing the default decorator configuration taken from the class attribute _retry_config"""
    _retry_config = minimal_retry_config_with_attempts(10)

    @retry
    async def _retryable_coroutine(self, thing):
        await asyncio.sleep(0.00001)
        return thing.go()

    @pytest.mark.asyncio
    async def test_max_attempts_reached_should_fail(self):
        thing = NoApiExceptionAfterCount(11, status=401)

        with pytest.raises(ApiException):
            await self._retryable_coroutine(thing)

        assert thing.counter == 10

    @pytest.mark.asyncio
    async def test_exception_not_matching_default_predicate_should_fail(self):
        thing = NoApiExceptionAfterCount(1, status=400)
        with pytest.raises(ApiException):
            await self._retryable_coroutine(thing)

        assert thing.counter == 1

    async def async_return_text(retry_state):
        await asyncio.sleep(0.00001)

        return "Calling %s keeps raising errors after %s attempts" % (
            retry_state.fn.__name__,
            retry_state.attempt_number,
        )

    @retry(stop=tenacity.stop_after_attempt(2),
           retry=tenacity.retry_if_exception(lambda e: True),
           retry_error_callback=async_return_text)
    async def _retryable_coroutine_with_custom_retry_error_callback(self, thing):
        await asyncio.sleep(0.00001)
        return thing.go()

    @pytest.mark.asyncio
    async def test_async_callback_error_retry(self):
        thing = NoIOErrorAfterCount(3)

        result = await self._retryable_coroutine_with_custom_retry_error_callback(thing)
        message = "Calling _retryable_coroutine_with_custom_retry_error_callback keeps raising errors after 2 attempts"
        assert result == message
