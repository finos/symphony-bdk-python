import asyncio

import pytest
import tenacity

from symphony.bdk.core.retry import retry
from symphony.bdk.gen import ApiException

from tests.core.config import minimal_retry_config_with_attempts
from tests.core.retry import NoIOErrorAfterCount, NoApiExceptionAfterCount, retry_test_decorator


@retry_test_decorator
async def _retryable_coroutine(thing):
    await asyncio.sleep(0.00001)
    return thing.go()


@retry_test_decorator(stop=tenacity.stop_after_attempt(2))
async def _retryable_coroutine_with_2_attempts(thing):
    await asyncio.sleep(0.00001)
    thing.go()


@pytest.mark.asyncio
async def test_async_retry():
    attempts = []

    async def async_retry(retry_state):
        if retry_state.outcome.failed:
            attempts.append((retry_state.outcome, retry_state.attempt_number))
            return True

        attempts.append((retry_state.outcome, retry_state.attempt_number))
        return False

    thing = NoIOErrorAfterCount(2)

    await _retryable_coroutine.retry_with(retry=async_retry)(thing)

    things, _ = zip(*attempts)
    assert len(attempts) == 3

    for thing in things[:-1]:
        with pytest.raises(IOError):
            thing.result()

    assert things[-1].result() is True


@pytest.mark.asyncio
async def test_async_callback_error_retry():
    async def async_return_text(retry_state):
        await asyncio.sleep(0.00001)

        return "Calling %s keeps raising errors after %s attempts" % (
            retry_state.fn.__name__,
            retry_state.attempt_number,
        )

    thing = NoIOErrorAfterCount(3)

    result = await _retryable_coroutine_with_2_attempts.retry_with(
        retry_error_callback=async_return_text
    )(thing)
    message = "Calling _retryable_coroutine_with_2_attempts keeps raising errors after 2 attempts"
    assert result == message


class TestDecoratorWrapper:
    """Testing the default decorator configuration taken from the class attribute _retry_config"""
    _retry_config = minimal_retry_config_with_attempts(10)

    @retry
    async def _retryable_coroutine(self, thing):
        await asyncio.sleep(0.00001)
        return thing.go()

    @retry(retry=tenacity.retry_if_result(lambda x: False))
    async def _non_retryable_coroutine(self, thing):
        return thing.go()

    @retry(stop=tenacity.stop_after_attempt(2))
    async def _retryable_coroutine_with_2_attempts(self, thing):
        await asyncio.sleep(0.00001)
        thing.go()

    @pytest.mark.asyncio
    async def test_max_attempts_reached_should_fail(self):
        thing = NoApiExceptionAfterCount(11, status=500)

        with pytest.raises(ApiException):
            await self._retryable_coroutine(thing)

        assert thing.counter == 10
        assert thing.call_count == 10

    @pytest.mark.asyncio
    async def test_exception_not_matching_default_predicate_should_fail(self):
        thing = NoApiExceptionAfterCount(1, status=400)
        with pytest.raises(ApiException):
            await self._retryable_coroutine(thing)

        assert thing.counter == 1
        assert thing.call_count == 1
