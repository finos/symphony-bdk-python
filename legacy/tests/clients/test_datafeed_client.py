import os
import unittest
from unittest.mock import patch

from sym_api_client_python.clients.datafeed_client import DataFeedClient
from sym_api_client_python.clients.datafeed_client_v1 import DataFeedClientV1
from sym_api_client_python.clients.datafeed_client_v2 import DataFeedClientV2
from sym_api_client_python.configure.configure import SymConfig


class TestDataFeedClient(unittest.TestCase):
    def setUp(self):
        self.config = SymConfig(get_path_relative_to_resources_folder('./bot-config.json'))
        self.config.load_config()

    def test_datafeed_client_v1(self):
        self.assert_configured_df_version_leads_to_df_client_type('v1', DataFeedClientV1)

    def test_datafeed_client_v2(self):
        self.assert_configured_df_version_leads_to_df_client_type('v2', DataFeedClientV2)

    def test_datafeed_client_wrong_version(self):
        self.assert_configured_df_version_leads_to_df_client_type('25', DataFeedClientV1)

    def assert_configured_df_version_leads_to_df_client_type(self, datafeed_version, expected_class):
        with patch('sym_api_client_python.clients.sym_bot_client.SymBotClient') as mock_client:
            self.config.data['datafeedVersion'] = datafeed_version
            mock_client.get_sym_config.return_value = self.config
            datafeed_client = DataFeedClient(mock_client)

            self.assertIsInstance(datafeed_client.datafeed_client, expected_class)


def get_path_relative_to_resources_folder(path_relative_to_resources):
    path_to_resources = os.path.join(os.path.dirname(__file__), '../resources/', path_relative_to_resources)
    return os.path.normpath(path_to_resources)

