import logging
from typing import Callable
from functools import wraps

from tenacity import stop_after_attempt, wait_exponential, before_sleep_log

from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig
from symphony.bdk.core.retry.strategy import refresh_session_if_unauthorized

from ._asyncio import AsyncRetrying


def retry(*dargs, **dkw):
    """A decorator that provides a mechanism to to retry failed requests
    Passed retry configuration arguments will override the default configuration defined in :py:meth:`decorator_f`
    If no _retry_config attribute is present in the decorated function instance, an AttributeError is raised.

    :param dargs: positional arguments passed to be added or to override the default configuration
    :param dkw: keyword arguments passed to be added or to override the default configuration
    """
    # support both @retry and @retry() as valid syntax
    if len(dargs) == 1 and callable(dargs[0]):
        return retry()(dargs[0])

    def retry_decorator(fun: Callable):
        @wraps(fun)
        def decorator_f(self, *args, **kwargs):
            """Fetches a BdkRetryConfiguration object from the instance of the called function and constructs the
            arguments for the AsyncRetrying object.
            """
            default_kwargs = {}
            retry_config: BdkRetryConfig = getattr(self, '_retry_config')
            logger = logging.getLogger(self.__module__)
            _before_sleep = before_sleep_log(logger, logging.INFO)
            default_kwargs.update(dict(before_sleep=_before_sleep))
            if retry_config is not None:
                config_kwargs = dict(retry=refresh_session_if_unauthorized,
                                     wait=wait_exponential(multiplier=retry_config.multiplier,
                                                           min=retry_config.initial_interval.total_seconds(),
                                                           max=retry_config.max_interval.total_seconds()),
                                     stop=stop_after_attempt(retry_config.max_attempts),
                                     reraise=True)
                default_kwargs.update(config_kwargs)
            # update default arguments by the ones passed as parameters
            default_kwargs.update(**dkw)
            return AsyncRetrying(*dargs, **default_kwargs).wraps(fun)(self, *args, **kwargs)

        return decorator_f

    return retry_decorator
