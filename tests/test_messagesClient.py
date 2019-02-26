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

#TestMessages class extends unittest class
#setUp functions executes before every test function runs --> grabs necessary data to run each client test
#streamId is hard coded --> replace with your own streamId to test if necessary
#execute by navigating to tests folder --> type 'python3 -m unittest discover' in commandline to execute each test
#comment any function that you no longer wish to test
class TestMessages(unittest.TestCase):

    def setUp(self):
        #go thorugh auth and config and then call function on message client
        logging.debug('hi')
        #RSA Auth flow:
        configure = SymConfig('sym_api_client_python/resources/rsa_config.json')
        configure.load_rsa_config()
        auth = SymBotRSAAuth(configure)
        auth.authenticate()
        #initialize SymBotClient with auth and configure objects
        self.botClient = SymBotClient(auth, configure)
        self.streamId = 'GVYRWwxRnEI7xde31EQz63___prrBEtgdA'

    # def test_blah (self):
    #     self.assertEqual(1, 1)

    # def test_createMessage(self):
    #     print('testing create messages function')
    #     message = dict(message = '<messageML><hash tag="reed"/></messageML>')
    #     self.assertTrue(self.bot_client.msg_client.send_msg(self.streamId, message))

    # def test_getMessageFromStream(self):
    #     print('testing get_msg_from_stream function')
    #     self.assertTrue(self.bot_client.msg_client.get_msg_from_stream(self.streamId, 0))
#
#     def test_getMessageAttachments(self):
#         pass
#
#     def test_importMessage(self):
#         pass
#
#     #this function returns a 200 but its empty
#     def test_postMessageSearch(self):
#         print('testing post Message search fucntion')
#         self.assertTrue(self.bot_client.msg_client.post_msg_search())
#
#     def test_getMessageSearch(self):
#         print('testing getMessage Search function')
#         self.assertTrue(self.bot_client.msg_client.get_msg_search())
#
    # def test_getMessageStatus(self):
    #     print('testing getMessage Status function')
    #     self.assertTrue(self.bot_client.msg_client.get_msg_status('7NcvR6mY9V2iXME5jT1DVn___prq9E3LbQ'))
#
    # def test_getSupportedAttachmentTypes(self):
    #     print('testing getAttachmentType function')
    #     self.assertTrue(self.bot_client.msg_client.get_supported_attachment_types())
#
#
# if __name__ == '__main__':
#     unittest.main()
