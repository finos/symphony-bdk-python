import unittest
import requests
import json
import logging
logging.basicConfig(filename='sym_api_client_python/logs/example.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)
from sym_api_client_python.configure.configure import SymConfig
from sym_api_client_python.auth.auth import Auth
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.listeners.im_listener_test_imp import IMListenerTestImp
from sym_api_client_python.listeners.room_listener_test_imp import RoomListenerTestImp

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
        logging.debug('hi')
        #RSA Auth flow:
        configure = SymConfig('sym_api_client_python/resources/rsa_config.json')
        configure.load_rsa_config()
        auth = SymBotRSAAuth(configure)
        auth.authenticate()
        #initialize SymBotClient with auth and configure objects
        self.botClient = SymBotClient(auth, configure)

    #pass
    # def test_getUserFromUsername(self):
    #     print('testing get_user_from_user_name function')
    #     self.assertTrue(self.bot_client.user_client.getUserFromUsername('bottleBot'))

    #pass
    # def test_getUserFromEmail(self):
    #     print('testing get_user_from_email function')
    #     self.assertTrue(self.bot_client.user_client.get_user_from_email('bottleBot@symphony.com'))

    #pass
    # def test_getUserFromId(self):
    #     print('testing get_user_from_id function')
    #     self.assertTrue(self.bot_client.user_client.get_user_from_id('344147139494909'))

    #pass
    # def test_getUsersFromIdList(self):
    #     print('testing get_users_from_id_list function')
    #     self.assertTrue(self.bot_client.user_client.get_users_from_id_list(['344147139494862', '344147139494909']))

    #pass
    # def test_getUsersFromEmailList(self):
    #     print('testing get_users_from_email_list function')
    #     self.assertTrue(self.bot_client.user_client.get_users_from_email_list(['reed.feldman@symphony.com','bottleBot@symphony.com']))

    #pass
    # def test_searchUsers(self):
    #     print('testing search users function')
    #     self.assertTrue(self.bot_client.user_client.search_users('reed feldman'))

# if __name__ == '__main__':
#     unittest.main()
