import sys

from symphony.bdk.core.config.model.bdk_datahose_config import BdkDatahoseConfig
from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig


def test_empty_datahose_config():
    datahose_config = BdkDatahoseConfig(None)
    assert datahose_config.tag is None
    assert datahose_config.event_types is None
    assert datahose_config.retry.max_attempts == sys.maxsize
    assert datahose_config.retry.multiplier == BdkRetryConfig.DEFAULT_MULTIPLIER


def test_datahose_config_with_retry():
    config_with_tag = {"tag": "TAG", "eventTypes": ["SOCIALMESSAGE", "CREATE_ROOM"]}
    config_retry = {"maxAttempts": 10, "multiplier": 1.51, "maxIntervalMillis": 10000, "initialIntervalMillis": 2000}
    config_with_tag["retry"] = config_retry

    datahose_config = BdkDatahoseConfig(config_with_tag)
    assert datahose_config.tag == "TAG"
    assert datahose_config.event_types == ["SOCIALMESSAGE", "CREATE_ROOM"]
    assert datahose_config.retry.max_attempts == 10
    assert datahose_config.retry.multiplier == 1.51
    assert datahose_config.retry.max_interval.seconds == 10
    assert datahose_config.retry.initial_interval.seconds == 2


def test_datahose_config_without_retry():
    config_with_tag = {"tag": "TAG", "eventTypes": ["SOCIALMESSAGE", "CREATE_ROOM"]}

    datahose_config = BdkDatahoseConfig(config_with_tag)
    assert datahose_config.tag == "TAG"
    assert datahose_config.event_types == ["SOCIALMESSAGE", "CREATE_ROOM"]
    assert datahose_config.retry.max_attempts == sys.maxsize
    assert datahose_config.retry.multiplier == BdkRetryConfig.DEFAULT_MULTIPLIER
