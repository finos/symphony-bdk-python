import pytest

from symphony.bdk.core.auth.jwt_helper import create_signed_jwt
from symphony.bdk.core.config.model.bdk_rsa_key_config import BdkRsaKeyConfig
from tests.utils.resource_utils import get_resource_filepath


@pytest.fixture()
def key_config():
    return BdkRsaKeyConfig()


def test_create_signed_jwt(key_config):
    key_config.path = get_resource_filepath('key/private_key.pem')

    assert create_signed_jwt(key_config, "test_bot") is not None


def test_create_signed_jwt_from_content(key_config):
    key_config.content = get_resource_filepath('key/private_key.pem', as_text=False).read_text()

    assert create_signed_jwt(key_config, "test_bot") is not None
