from unittest.mock import patch
from asyncmock import AsyncMock

import pytest

from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.config.bdk_config_loader import BdkConfigLoader
from tests.utils.resource_utils import get_config_resource_filepath


@pytest.fixture()
def config():
    return BdkConfigLoader.load_from_file(get_config_resource_filepath("config.yaml"))


def test_get_api_client(config):
    with patch('symphony.bdk.core.client.api_client_factory.ApiClient', autospec=True):
        api_client_factory = ApiClientFactory(config)
        assert api_client_factory.get_pod_client() is not None
        assert api_client_factory.get_login_client() is not None
        assert api_client_factory.get_agent_client() is not None
        assert api_client_factory.get_session_auth_client() is not None
        assert api_client_factory.get_relay_client() is not None
