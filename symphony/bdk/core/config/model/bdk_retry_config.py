import sys
from datetime import timedelta


class BdkRetryConfig:
    """Class containing the retry configuration"""
    INFINITE_MAX_ATTEMPTS = -1
    DEFAULT_MAX_ATTEMPTS = 10
    DEFAULT_INITIAL_INTERVAL = 500
    DEFAULT_MULTIPLIER = 2
    DEFAULT_MAX_INTERVAL = 5 * 60 * 1000

    def __init__(self, config=None):
        if config is None:
            config = {}

        self.max_attempts = config.get("maxAttempts", self.DEFAULT_MAX_ATTEMPTS)
        if self.max_attempts < 0:
            self.max_attempts = sys.maxsize
        self.initial_interval = timedelta(milliseconds=config.get("initialIntervalMillis",
                                                                  self.DEFAULT_INITIAL_INTERVAL))
        self.multiplier = config.get("multiplier", self.DEFAULT_MULTIPLIER)
        if self.multiplier < 1:
            self.multiplier = self.DEFAULT_MULTIPLIER
        self.max_interval = timedelta(milliseconds=config.get("maxIntervalMillis", self.DEFAULT_MAX_INTERVAL))
