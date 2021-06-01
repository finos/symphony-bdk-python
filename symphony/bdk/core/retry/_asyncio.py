import asyncio

try:
    from inspect import iscoroutinefunction
except ImportError:
    iscoroutinefunction = None

import sys


import six

from tenacity import AttemptManager, RetryAction, TryAgain
from tenacity import BaseRetrying
from tenacity import DoAttempt
from tenacity import DoSleep
from tenacity import RetryCallState


class AsyncRetrying(BaseRetrying):
    """This is a modified version of the tenacity.AsyncRetrying class that handles asynchronously defined retry or
    retry_error_callback parameters.

    There is an open PR for this change on the tenacity repository: https://github.com/jd/tenacity/pull/289
    """
    def __init__(self, sleep=asyncio.sleep, **kwargs):
        super().__init__(**kwargs)
        self.sleep = sleep

    async def iter(self, retry_state):
        fut = retry_state.outcome
        if fut is None:
            if self.before is not None:
                self.before(retry_state)
            return DoAttempt()

        is_explicit_retry = retry_state.outcome.failed and isinstance(
            retry_state.outcome.exception(), TryAgain
        )
        if iscoroutinefunction(self.retry):
            should_retry = await self.retry(retry_state=retry_state)
        else:
            should_retry = self.retry(retry_state=retry_state)
        if not (is_explicit_retry or should_retry):
            return fut.result()

        if self.after is not None:
            self.after(retry_state=retry_state)

        self.statistics["delay_since_first_attempt"] = retry_state.seconds_since_start
        if self.stop(retry_state=retry_state):
            if self.retry_error_callback:
                if iscoroutinefunction(self.retry_error_callback):
                    return await self.retry_error_callback(retry_state=retry_state)
                return self.retry_error_callback(retry_state=retry_state)
            retry_exc = self.retry_error_cls(fut)
            if self.reraise:
                raise retry_exc.reraise()
            six.raise_from(retry_exc, fut.exception())

        if self.wait:
            iteration_sleep = self.wait(retry_state=retry_state)
        else:
            iteration_sleep = 0.0
        retry_state.next_action = RetryAction(iteration_sleep)
        retry_state.idle_for += iteration_sleep
        self.statistics["idle_for"] += iteration_sleep
        self.statistics["attempt_number"] += 1

        if self.before_sleep is not None:
            self.before_sleep(retry_state=retry_state)

        return DoSleep(iteration_sleep)

    async def __call__(self, fn, *args, **kwargs):
        self.begin(fn)

        retry_state = RetryCallState(retry_object=self, fn=fn, args=args, kwargs=kwargs)
        while True:
            do = await self.iter(retry_state=retry_state)
            if isinstance(do, DoAttempt):
                try:
                    result = await fn(*args, **kwargs)
                except BaseException:
                    retry_state.set_exception(sys.exc_info())
                else:
                    retry_state.set_result(result)
            elif isinstance(do, DoSleep):
                retry_state.prepare_for_next_attempt()
                await self.sleep(do)
            else:
                return do

    def __aiter__(self):
        self.begin(None)
        self._retry_state = RetryCallState(self, fn=None, args=(), kwargs={})
        return self

    async def __anext__(self):
        while True:
            do = await self.iter(retry_state=self._retry_state)
            if do is None:
                raise StopAsyncIteration
            if isinstance(do, DoAttempt):
                return AttemptManager(retry_state=self._retry_state)
            if isinstance(do, DoSleep):
                self._retry_state.prepare_for_next_attempt()
                await self.sleep(do)
            else:
                return do

    def wraps(self, fn):
        fn = super().wraps(fn)

        # Ensure wrapper is recognized as a coroutine function.

        async def async_wrapped(*args, **kwargs):
            return await fn(*args, **kwargs)

        # Preserve attributes
        async_wrapped.retry = fn.retry
        async_wrapped.retry_with = fn.retry_with

        return async_wrapped
