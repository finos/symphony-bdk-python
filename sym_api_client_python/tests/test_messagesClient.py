import unittest
import requests
import json
from ..clients.SymBotClient import SymBotClient
from ..clients.MessageClient import MessageClient
from ..listeners.imListenerTestImp import IMListenerTestImp
from ..listeners.roomListenerTestImp import RoomListenerTestImp
from ..configure.configure import Config
from ..auth.auth import Auth

#TestMessages class extends unittest class
#setUp functions executes before every test function runs --> grabs necessary data to run each client test
#streamId is hard coded --> replace with your own streamId to test if necessary
#execute by navigating to tests folder --> type 'python3 -m unittest discover' in commandline to execute each test
#comment any function that you no longer wish to test
class TestMessages(unittest.TestCase):

    def setUp(self):
        #go thorugh auth and config and then call function on message client
        configure = Config('./resources/config.json')
        configure.connect()
        auth = Auth(configure)
        auth.authenticate()
        self.botClient = SymBotClient(auth, configure)
        self.streamId = 'NyLNtKZwstZLapBgzR1Nqn___pt1T1EpdA'

    # def test_blah (self):
    #     self.assertEqual(1, 1)

    # def test_createMessage(self):
    #     print('testing create messages function')
    #     message = dict(message = '<messageML>Hi {}!</messageML>'.format('Reed'))
    #     self.assertTrue(self.botClient.messageClient.createMessage(self.streamId, message ))

    def test_getMessage(self):
        print('testing getMessage function')
        self.assertTrue(self.botClient.messageClient.getMessages(self.streamId, 0))
#
#     def test_getAttachments(self):
#         pass
#
#     def test_importMessage(self):
#         pass
#
#     #this function returns a 200 but its empty
#     def test_postMessageSearch(self):
#         print('testing post Message search fucntion')
#         self.assertTrue(self.botClient.messageClient.postMessageSearch())
#
#     def test_getMessageSearch(self):
#         print('testing getMessage Search function')
#         self.assertTrue(self.botClient.messageClient.getMessageSearch())
#
#     def test_getMessageStatus(self):
#         print('testing getMessage Status function')
#         self.assertTrue(self.botClient.messageClient.getMessageStatus('9930CkBb0j2l4d0RPq9rC3___pt2etu0bQ'))
#
#     def test_getAttachmentTypes(self):
#         print('testing getAttachmentType function')
#         self.assertTrue(self.botClient.messageClient.getAttachmentTypes())
#
#
# if __name__ == '__main__':
#     unittest.main()
