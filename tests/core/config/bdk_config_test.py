from symphony.bdk.core.config.loader import BdkConfigLoader

from tests.utils.resource_utils import get_config_resource_filepath
import pytest

@pytest.fixture(params=["config.json", "config.yaml"])
def simple_config_path(request):
    return get_config_resource_filepath(request.param)

def test_update_privateKey(simple_config_path):
    config = BdkConfigLoader.load_from_file(simple_config_path)
    previousPK = config.bot.private_key
    previousCert = config.bot.certificate
    config.setBotConfig(privateKey="/path/to/privateKey")
    assert config.bot.private_key != previousPK
    assert config.bot.certificate == previousCert

def test_update_certificate(simple_config_path):
    config = BdkConfigLoader.load_from_file(simple_config_path)
    previousPK = config.bot.private_key
    previousCert = config.bot.certificate
    config.setBotConfig(certificate="/path/to/cert")
    assert config.bot.private_key == previousPK
    assert config.bot.certificate != previousCert

def test_update_privateKey_and_certificate(simple_config_path):
    config = BdkConfigLoader.load_from_file(simple_config_path)
    previousPK = config.bot.private_key
    previousCert = config.bot.certificate
    config.setBotConfig(privateKey="/path/to/privateKey", certificate="/path/to/cert")
    assert config.bot.private_key != previousPK
    assert config.bot.certificate != previousCert
