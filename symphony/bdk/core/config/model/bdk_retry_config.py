import sys


class BdkRetryConfig:
    """Class containing the retry configuration"""
    INFINITE_MAX_ATTEMPTS = -1
    DEFAULT_MAX_ATTEMPTS = 10
    DEFAULT_INITIAL_INTERVAL = 0.5
    DEFAULT_MULTIPLIER = 2
    DEFAULT_MAX_INTERVAL = 5 * 60

    def __init__(self, config=None, max_attempts=None):
        if config is None:
            config = {}

        self._max_attempts = config.get("maxAttempts") if "maxAttempts" in config else max_attempts
        self._initial_interval = config.get("initialIntervalMillis")
        self._multiplier = config.get("multiplier")
        self._max_interval = config.get("maxIntervalMillis")

    @property
    def max_attempts(self):
        if self._max_attempts is None:
            return self.DEFAULT_MAX_ATTEMPTS
        if self._max_attempts < 0:  # Negative value means an infinite number of attempts
            return sys.maxsize
        return self._max_attempts

    @max_attempts.setter
    def max_attempts(self, value):
        self._max_attempts = value

    @property
    def initial_interval(self):
        if self._initial_interval is None:
            return self.DEFAULT_INITIAL_INTERVAL
        return self._initial_interval / 1000

    @initial_interval.setter
    def initial_interval(self, value):
        self._initial_interval = value

    @property
    def multiplier(self):
        if self._multiplier is None or self._multiplier < 1:
            return self.DEFAULT_MULTIPLIER
        return self._multiplier

    @multiplier.setter
    def multiplier(self, value):
        self._multiplier = value

    @property
    def max_interval(self):
        if self._max_interval is None:
            return self.DEFAULT_MAX_INTERVAL
        return self._max_interval / 1000

    @max_interval.setter
    def max_interval(self, value):
        self._max_interval = value
