from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig


def minimal_retry_config():
    retry_config = BdkRetryConfig()
    retry_config.multiplier = 1
    retry_config.initial_interval = 10
    retry_config.max_interval = 10
    retry_config.max_attempts = 1
    return retry_config


def minimal_retry_config_with_attempts(max_attempts: int):
    retry_config = BdkRetryConfig()
    retry_config.multiplier = 1
    retry_config.initial_interval = 10
    retry_config.max_interval = 10
    retry_config.max_attempts = max_attempts
    return retry_config