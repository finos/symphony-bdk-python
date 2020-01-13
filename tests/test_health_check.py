import logging
import unittest
from unittest.mock import patch

from sym_api_client_python.loaders import load_from_env_var
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.configure.configure import SymConfig

class TestHealthCheck(unittest.TestCase):

    # Unlike setUp this only fires once per class
    @classmethod
    def setUpClass(cls):
        logging.debug('testing health_check file:')
        try:
            conf, auth = load_from_env_var("SYMPHONY_TEST_CONFIG")
            cls.configure = conf
            cls.auth = auth
        except ValueError:
            #RSA Auth flow:
            cls.configure = SymConfig('sym_api_client_python/resources/config.json')
            cls.configure.load_config()
            cls.auth = SymBotRSAAuth(cls.configure)
            cls.auth.authenticate()

        # Initialize SymBotClient with auth and configure objects
        cls.bot_client = SymBotClient(cls.auth, cls.configure)

    def test_do_health_check(self):
        client = self.bot_client.get_health_check_client()
        print(client.get_health_check())
    
    # This isn't a great test of the SDK, it just checks the local services
    def test_ensure_services(self):
        client = self.bot_client.get_health_check_client()
        client.ensure_all_services_up()

    def test_specific_ensure_services(self):
        client = self.bot_client.get_health_check_client()
        client.ensure_all_services_up(fields_to_check=["podConnectivity"])

    @patch('sym_api_client_python.clients.health_check_client.HealthCheckClient.get_health_check', autospec=True)
    def test_ensure_services_throws(self, health_check):
        health_check.return_value = {'podConnectivity': False,
                'keyManagerConnectivity': True,
                'encryptDecryptSuccess': True,
                'agentServiceUser': True,
                'ceServiceUser': True}
        client = self.bot_client.get_health_check_client()
        with self.assertRaises(RuntimeError):
            client.ensure_all_services_up()

    @patch('sym_api_client_python.clients.health_check_client.HealthCheckClient.get_health_check', autospec=True)
    def test_ensure_services_throws(self, health_check):
        health_check.return_value = {'podConnectivity': False,
                'keyManagerConnectivity': True,
                'encryptDecryptSuccess': True,
                'agentServiceUser': True,
                'ceServiceUser': True}
        client = self.bot_client.get_health_check_client()
        client.ensure_all_services_up(fields_to_check=["ceServiceUser", "agentServiceUser"])

