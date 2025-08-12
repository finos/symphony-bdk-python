from symphony.bdk.core.retry import AsyncRetrying
from symphony.bdk.gen import ApiException


class FixedChainedExceptions:
    """Holds counter state and exceptions to throw for invoking a method several times in a row."""

    def __init__(self, exception_list):
        self.counter = 0
        self.call_count = 0
        self.exception_list = exception_list
        self.count = len(self.exception_list)

    def go(self):
        """Raise the exceptions in exception_list consecutively for each call

        Then return True
        """
        self.call_count += 1
        if self.counter < self.count:
            self.counter += 1
            raise self.exception_list[self.counter - 1]
        return True

    def reset(self):
        """Resets counter for FixedChainedExceptions instance

        :return:
        """
        self.call_count = 0
        self.counter = 0


class NoApiExceptionAfterCount:
    """Holds counter state for invoking a method several times in a row."""

    def __init__(self, count, status=400):
        self.counter = 0
        self.call_count = 0
        self.count = count
        self.status = status

    def go(self):
        """Raise an ApiException until after count threshold has been crossed.

        Then return True.
        """
        self.call_count += 1
        if self.counter < self.count:
            self.counter += 1
            raise ApiException(status=self.status, reason="Hi there, I'm an ApiException")
        return True


class NoIOErrorAfterCount:
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


def retry_test_decorator(*dargs, **dkw):
    """Wrap a function with a `AsyncRetrying` object.

    :param dargs: positional arguments passed to Retrying object
    :param dkw: keyword arguments passed to the Retrying object
    """
    # support both @retry and @retry() as valid syntax
    if len(dargs) == 1 and callable(dargs[0]):
        return retry_test_decorator()(dargs[0])

    def wrap(f):
        return AsyncRetrying(*dargs, **dkw).wraps(f)

    return wrap
