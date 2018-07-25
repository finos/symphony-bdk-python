import unittest
import requests
import json
from ..clients.UserClient import UserClient
from ..clients.SymBotClient import SymBotClient
from ..listeners.imListenerTestImp import IMListenerTestImp
from ..listeners.roomListenerTestImp import RoomListenerTestImp
from ..configure.configure import Config
from ..auth.auth import Auth

#TestUsers class extends unittest class
#setUp functions executes before every test function runs --> grabs necessary data to run each client test
#streamId is hard coded --> replace with your own streamId to test if necessary
#execute by navigating to tests folder --> type 'python3 -m unittest discover' in commandline to execute each test
#comment any function that you no longer wish to test
class TestUsers(unittest.TestCase):

    def setUp(self):
        configure = Config('./resources/config.json')
        configure.connect()
        auth = Auth(configure)
        auth.authenticate()
        self.botClient = SymBotClient(auth, configure)

    #pass
    # def test_getUsersV3(self):
    #     print('testing get users function v3')
    #     self.assertTrue(self.botClient.userClient.getUsersV3(['344147139494083', '344147139494588', '344147139494862']))

    #pass --> make sure to only pass one user to usersArray in V2
    # def test_getUsersV2(self):
    #     print('testing get users function v2')
    #     self.assertTrue(self.botClient.userClient.getUsersV2(['344147139494083']))

    #pass
    # def test_searchUsers(self):
    #     print('testing search users function')
    #     self.assertTrue(self.botClient.userClient.searchUsers('reed feldman'))

if __name__ == '__main__':
    unittest.main()
