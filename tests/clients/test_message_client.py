import os
import unittest
from io import IOBase

from sym_api_client_python.clients.message_client import open_file


def get_path_to_file():
    path_to_resources = os.path.join(os.path.dirname(__file__), '../resources/bot-config.json')
    return os.path.normpath(path_to_resources)


class TestMessageClient(unittest.TestCase):
    def test_open_file_with_filename(self):
        path = get_path_to_file()
        with open_file(path) as file:
            self.assertIsInstance(file, IOBase)
            self.assertTrue(file.readable())
        self.assertTrue(file.closed)

    def test_open_file_with_opened_file(self):
        path = get_path_to_file()
        with open(path) as file:
            with open_file(file) as opened_file:
                self.assertEqual(file, opened_file)
