from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig

TAG = "tag"
EVENT_TYPES = "eventTypes"
RETRY = "retry"


class BdkDatahoseConfig:
    """Class holding datahose specific configuration.
    """

    def __init__(self, config):
        """

        :param config: the dict containing the datahose specific configuration.
        """
        self.tag = None
        self.event_types = None
        self.retry = BdkRetryConfig(dict(maxAttempts=BdkRetryConfig.INFINITE_MAX_ATTEMPTS))
        if config is not None:
            self.tag = config.get(TAG)
            self.event_types = config.get(EVENT_TYPES)
            if RETRY in config:
                self.retry = BdkRetryConfig(config.get(RETRY))
