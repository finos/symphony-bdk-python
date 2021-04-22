import sys
import pytest

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig

from tests.utils.resource_utils import get_config_resource_filepath
from tests.utils.resource_utils import get_resource_filepath


@pytest.fixture(name="simple_config_path", params=["config.json", "config.yaml"])
def fixture_simple_config_path(request):
    return get_config_resource_filepath(request.param)


def test_update_private_key(simple_config_path):
    config = BdkConfigLoader.load_from_file(simple_config_path)
    private_key = get_resource_filepath("key/private_key.pem", as_text=False).read_text()
    config.bot.private_key.content = private_key
    assert config.bot.private_key._content == private_key
    assert config.bot.private_key._path is None


def test_update_certificate(simple_config_path):
    config = BdkConfigLoader.load_from_file(simple_config_path)
    certificate_path = get_resource_filepath("cert/certificate.cert", as_text=True)
    config.bot.certificate.path = certificate_path
    assert config.bot.certificate._path == certificate_path


def test_retry_configuration():
    config_path = get_config_resource_filepath("retry_config.yaml")
    config = BdkConfigLoader.load_from_file(config_path)

    assert config.retry.max_attempts == 2
    assert config.retry.initial_interval == 1.0
    assert config.retry.multiplier == 3
    assert config.retry.max_interval == 2.0


def test_default_retry_configuration():
    config_path = get_config_resource_filepath("config.yaml")
    config = BdkConfigLoader.load_from_file(config_path)

    assert config.retry.max_attempts == BdkRetryConfig.DEFAULT_MAX_ATTEMPTS
    assert config.retry.initial_interval == BdkRetryConfig.DEFAULT_INITIAL_INTERVAL
    assert config.retry.multiplier == BdkRetryConfig.DEFAULT_MULTIPLIER
    assert config.retry.max_interval == BdkRetryConfig.DEFAULT_MAX_INTERVAL

    # Datafeed default retry
    assert config.datafeed.retry.max_attempts == sys.maxsize
    assert config.datafeed.retry.initial_interval == BdkRetryConfig.DEFAULT_INITIAL_INTERVAL
    assert config.datafeed.retry.multiplier == BdkRetryConfig.DEFAULT_MULTIPLIER
    assert config.datafeed.retry.max_interval == BdkRetryConfig.DEFAULT_MAX_INTERVAL


def test_datafeed_retry_configuration():
    config_path = get_config_resource_filepath("datafeed_retry_config.yaml")
    config = BdkConfigLoader.load_from_file(config_path)

    assert config.datafeed.retry.max_attempts == 2
    assert config.datafeed.retry.initial_interval == 1.0
    assert config.datafeed.retry.multiplier == 3
    assert config.datafeed.retry.max_interval == 2.0
