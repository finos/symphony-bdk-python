import unittest
import requests
import json
import logging
logging.basicConfig(filename='sym_api_client_python/logs/example.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)
from sym_api_client_python.configure.configure import SymConfig
from sym_api_client_python.auth.auth import Auth
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.SymBotClient import SymBotClient
from sym_api_client_python.listeners.imListenerTestImp import IMListenerTestImp
from sym_api_client_python.listeners.roomListenerTestImp import RoomListenerTestImp

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
        configure.loadFromRSA()
        auth = SymBotRSAAuth(configure)
        auth.authenticate()
        #initialize SymBotClient with auth and configure objects
        self.botClient = SymBotClient(auth, configure)

    #pass
    # def test_getUserFromUsername(self):
    #     print('testing getUserFromUserName function')
    #     self.assertTrue(self.botClient.userClient.getUserFromUsername('bottleBot'))

    #pass
    # def test_getUserFromEmail(self):
    #     print('testing getUserFromEmail function')
    #     self.assertTrue(self.botClient.userClient.getUserFromEmail('bottleBot@symphony.com'))

    #pass
    # def test_getUserFromId(self):
    #     print('testing getUserFromId function')
    #     self.assertTrue(self.botClient.userClient.getUserFromId('344147139494909'))

    #pass
    # def test_getUsersFromIdList(self):
    #     print('testing getUsersFromIdList function')
    #     self.assertTrue(self.botClient.userClient.getUsersFromIdList(['344147139494862', '344147139494909']))

    #pass
    # def test_getUsersFromEmailList(self):
    #     print('testing getUsersFromEmailList function')
    #     self.assertTrue(self.botClient.userClient.getUsersFromEmailList(['reed.feldman@symphony.com','bottleBot@symphony.com']))

    #pass
    # def test_searchUsers(self):
    #     print('testing search users function')
    #     self.assertTrue(self.botClient.userClient.searchUsers('reed feldman'))

# if __name__ == '__main__':
#     unittest.main()
