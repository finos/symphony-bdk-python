import pytest

from symphony.bdk.core.config.model.bdk_client_config import BdkClientConfig
from symphony.bdk.core.config.model.bdk_server_config import BdkServerConfig


@pytest.fixture(name="parent_config", scope="module")
def fixture_parent_config():
    parent_config_dict = {
        "scheme": "parent_scheme",
        "host": "parent_host",
        "port": 0000,
        "context": "parent_context",
    }
    return BdkServerConfig(**parent_config_dict)


def test_empty_client(parent_config):
    """Should get the client_config attributes from the parent config if not defined"""
    empty_config_dict = {}
    client_config = BdkClientConfig(parent_config, empty_config_dict)

    assert client_config.scheme == "parent_scheme"
    assert client_config.host == "parent_host"
    assert client_config.port == 0000
    assert client_config.context == "parent_context"


def test_full_client(parent_config):
    """Should get the client_config attributes from the client config when defined"""
    client_config_dict = {
        "scheme": "client_scheme",
        "host": "client_host",
        "port": 1111,
        "context": "client_context",
    }
    client_config = BdkClientConfig(parent_config, client_config_dict)

    assert client_config.scheme == "client_scheme"
    assert client_config.host == "client_host"
    assert client_config.port == 1111
    assert client_config.context == "client_context"


def test_get_base_path_from_client(parent_config):
    client_config_dict = {"host": "dev.symphony.com", "port": 1234}
    client_config = BdkClientConfig(parent_config, client_config_dict)

    assert client_config.get_base_path() == "parent_scheme://dev.symphony.com:1234/parent_context"


def test_get_base_path_from_client_no_root():
    parent_config = BdkServerConfig()
    client_config_dict = {"host": "dev.symphony.com", "port": 1234}
    client_config = BdkClientConfig(parent_config, client_config_dict)

    assert client_config.get_base_path() == "https://dev.symphony.com:1234"
