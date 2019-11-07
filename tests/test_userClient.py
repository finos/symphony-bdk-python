import json
import logging
import unittest

import requests

from sym_api_client_python.auth.auth import Auth
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.configure.configure import SymConfig
from sym_api_client_python.listeners.im_listener_test_imp import IMListenerTestImp
from sym_api_client_python.listeners.room_listener_test_imp import RoomListenerTestImp
from sym_api_client_python.loaders import load_from_env_var

logging.basicConfig(filename='sym_api_client_python/logs/example.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# 344147139494862
# 344147139494909
# reed.feldman@symphony.com
# bottleBot@symphony.com

#TestUsers class extends unittest class
#setUp functions executes before every test function runs --> grabs necessary data to run each client test
#streamId is hard coded --> replace with your own streamId to test if necessary
#execute by navigating to tests folder --> type 'python3 -m unittest discover' in commandline to execute each test
#comment any function that you no longer wish to test
class TestUsers(unittest.TestCase):

    def setUp(self):
        try:
            conf, auth = load_from_env_var("SYMPHONY_TEST_CONFIG")
            self.configure = conf
            self.auth = auth
        except ValueError:
            #RSA Auth flow:
            self.configure = SymConfig('sym_api_client_python/resources/hackathon_config.json')
            self.configure.load_config()
            auth = SymBotRSAAuth(self.configure)
            auth.authenticate()

        # Initialize SymBotClient with auth and configure objects
        self.bot_client = SymBotClient(auth, self.configure)

    #pass
    def test_getUserFromUsername(self):
        print('testing get_user_from_user_name function')
        username = self.configure.data["botUsername"]
        self.assertTrue(self.bot_client.get_user_client().get_user_from_user_name(username))

    #pass
    def test_getUserFromEmail(self):
        print('testing get_user_from_email function')
        email = self.configure.data["botEmailAddress"]
        self.assertTrue(self.bot_client.get_user_client().get_user_from_email(email))

    #pass
    def test_getUserFromId(self):
        print('testing get_user_from_id function')
        self.assertTrue(self.bot_client.get_user_client().get_user_from_id('344147139494909'))

    #pass
    def test_getUsersFromIdList(self):
        print('testing get_users_from_id_list function')
        self.assertTrue(self.bot_client.get_user_client().get_users_from_id_list(['344147139494862', '344147139494909']))

    #pass
    def test_getUsersFromEmailList(self):
        print('testing get_users_from_email_list function')
        self.assertTrue(self.bot_client.get_user_client().get_users_from_email_list(['reed.feldman@symphony.com','bottleBot@symphony.com']))

    #pass
    def test_searchUsers(self):
        print('testing search users function')
        username = self.configure.data["botUsername"]
        # Make a search string by taking the first half of the username
        search_string = username[:int(len(username) / 2)]
        self.assertTrue(self.bot_client.get_user_client().search_users(search_string))

# if __name__ == '__main__':
#     unittest.main()
