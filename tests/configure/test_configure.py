import os
import unittest
from tests.util.resource_util import get_resource_filepath

from sym_api_client_python.configure.configure import SymConfig

class TestSymConfig(unittest.TestCase):

	def setUp(self):
		self.config = SymConfig(get_resource_filepath('./bot-config.json'))
		self.config.load_config()

	def test_context_path(self):
		self.assertEqual(self.config.data['sessionAuthHost'], "https://MY_ENVIRONMENT.symphony.com:443/sessionAuthContext")
		self.assertEqual(self.config.data['keyAuthHost'], "https://MY_ENVIRONMENT.symphony.com:443/keyAuthContext")
		self.assertEqual(self.config.data['podHost'], "https://MY_ENVIRONMENT.symphony.com:443/podContext")
		self.assertEqual(self.config.data['agentHost'], "https://MY_ENVIRONMENT.symphony.com:443")
