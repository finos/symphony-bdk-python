import sys

from symphony.bdk.core.config.model.bdk_datahose_config import BdkDatahoseConfig
from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig


def test_empty_datahose_config():
    datahose_config = BdkDatahoseConfig(None)
    assert datahose_config.tag is None
    assert datahose_config.filters is None
    assert datahose_config.retry.max_attempts == sys.maxsize
    assert datahose_config.retry.multiplier == BdkRetryConfig.DEFAULT_MULTIPLIER
