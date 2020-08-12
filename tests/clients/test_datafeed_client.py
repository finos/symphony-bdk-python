import pytest
from unittest.mock import patch

from sym_api_client_python.configure.configure import SymConfig
from sym_api_client_python.clients.datafeed_client import DataFeedClient
from sym_api_client_python.clients.datafeed_client_v1 import DataFeedClientV1
from sym_api_client_python.clients.datafeed_client_v2 import DataFeedClientV2


@pytest.fixture
def config():
    configure = SymConfig('./tests/resources/bot-config.json', __file__)
    configure.load_config()
    return configure


@patch('sym_api_client_python.clients.sym_bot_client.SymBotClient', autospec=True)
def test_datafeed_client_v1(mock_client, config):
    config.data["datafeedVersion"] = "v1"

    mock_client.get_sym_config.return_value = config

    # Initialize datafeed client
    datafeed_client = DataFeedClient(mock_client)

    assert isinstance(datafeed_client.datafeed_client, DataFeedClientV1) == True

@patch('sym_api_client_python.clients.sym_bot_client.SymBotClient', autospec=True)
def test_datafeed_client_v2(mock_client, config):
    config.data["datafeedVersion"] = "v2"

    mock_client.get_sym_config.return_value = config

    # Initialize datafeed client
    datafeed_client = DataFeedClient(mock_client)
    print(datafeed_client.datafeed_client)
    assert isinstance(datafeed_client.datafeed_client, DataFeedClientV2) == True

@patch('sym_api_client_python.clients.sym_bot_client.SymBotClient', autospec=True)
def test_datafeed_client_wrong_version(mock_client, config):
    config.data["datafeed_version"] = 25

    mock_client.get_sym_config.return_value = config

    # Initialize datafeed client
    datafeed_client = DataFeedClient(mock_client)

    assert isinstance(datafeed_client.datafeed_client, DataFeedClientV1) == True



