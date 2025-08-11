from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig


def minimal_retry_config():
    return BdkRetryConfig(
        dict(
            maxAttempts=1, initialIntervalMillis=10, maxIntervalMillis=10, multiplier=1
        )
    )


def minimal_retry_config_with_attempts(max_attempts: int):
    return BdkRetryConfig(
        dict(
            maxAttempts=max_attempts,
            initialIntervalMillis=10,
            maxIntervalMillis=10,
            multiplier=1,
        )
    )
