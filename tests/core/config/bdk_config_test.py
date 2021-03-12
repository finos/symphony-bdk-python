import pytest

from symphony.bdk.core.config.loader import BdkConfigLoader

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
    certificate = get_resource_filepath("cert/certificate.cert", as_text=False).read_text()
    config.bot.certificate.content = certificate
    assert config.bot.certificate._content == certificate
    assert config.bot.certificate._path is None
