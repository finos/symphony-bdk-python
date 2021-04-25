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