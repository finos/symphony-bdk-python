import unittest
import requests
import json
import logging
import asyncio
import io

logging.basicConfig(filename='sym_api_client_python/logs/example.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)

from sym_api_client_python.configure.configure import SymConfig
from sym_api_client_python.auth.auth import Auth
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.listeners.im_listener_test_imp import IMListenerTestImp
from sym_api_client_python.listeners.room_listener_test_imp import RoomListenerTestImp
from sym_api_client_python.loaders import load_from_env_var

#TestMessages class extends unittest class
#setUp functions executes before every test function runs --> grabs necessary data to run each client test
#streamId is hard coded --> replace with your own streamId to test if necessary
#execute by navigating to tests folder --> type 'python3 -m unittest discover' in commandline to execute each test
#comment any function that you no longer wish to test
class TestMessages(unittest.TestCase):

    def setUp(self):
        try:
            conf, auth = load_from_env_var("SYMPHONY_TEST_CONFIG")
            self.configure = conf
            self.auth = auth
        except ValueError:
            #RSA Auth flow:
            self.configure = SymConfig('sym_api_client_python/resources/config.json')
            self.configure.load_config()
            auth = SymBotRSAAuth(self.configure)
            auth.authenticate()

        #initialize SymBotClient with auth and configure objects
        self.bot_client = SymBotClient(self.auth, self.configure)
        self.streamId = 'ychiFHXta__zF7YqoLOnN3___pBQNr6mdA'
        self.messageId = 'g05bspw5c5E7Aq2SMZjIJX___o_KIUG2bQ'
        self.test_message = dict(message = '<messageML><hash tag="reed"/></messageML>')
        self.params = {"text" : "hi", "streamId" : "ychiFHXta__zF7YqoLOnN3___pBQNr6mdA"}

    def test_createMessage(self):
        print('testing create messages function')
        message = self.test_message
        self.assertTrue(self.bot_client.get_message_client().send_msg(self.streamId, message))

    def test_create_message_async(self):
        asyncio.get_event_loop().run_until_complete(
            self.bot_client.get_message_client().send_msg_async(self.streamId, self.test_message)
            )

    def test_getMessageFromStream(self):
        print('testing get_msg_from_stream function')
        self.assertTrue(self.bot_client.get_message_client().get_msg_from_stream(self.streamId, 0))

    def test_get_message_from_stream_async(self):
        asyncio.get_event_loop().run_until_complete(
            self.bot_client.get_message_client().get_msg_from_stream_async(self.streamId, 0)
            )

    def test_create_message_attachment(self):
        fp = __file__
        self.bot_client.get_message_client().send_msg_with_attachment(
            self.streamId, self.test_message["message"], "testfilename.txt", fp
            )

    def test_create_message_attachment_iostream(self):
        file_like_object = io.StringIO("This is a test")
        self.bot_client.get_message_client().send_msg_with_attachment(
            self.streamId, self.test_message["message"], "testfilename.txt", file_like_object
            )

    def test_create_message_attachment_async(self):
        file_like_object = io.StringIO("This is a test")
        asyncio.get_event_loop().run_until_complete(
            self.bot_client.get_message_client().send_msg_with_attachment_async(
                self.streamId, self.test_message["message"], "testfilename.txt", file_like_object
            )
        )
    def test_create_message_attachment_iostream_async(self):
        file_like_object = io.StringIO("This is a test")
        asyncio.get_event_loop().run_until_complete(
            self.bot_client.get_message_client().send_msg_with_attachment_async(
                self.streamId, self.test_message["message"], "testfilename.txt", file_like_object
            )
        )
    def test_getMessageAttachments(self):
        pass

    def test_importMessage(self):
        pass

    #this function returns a 200 but its empty
    def test_postMessageSearch(self):
        print('testing post Message search function')
        self.assertTrue(self.bot_client.get_message_client().post_msg_search(self.params))

    def test_getMessageSearch(self):
        print('testing getMessage Search function')
        self.assertTrue(self.bot_client.get_message_client().get_msg_search({'streamId' : self.streamId, 'text'}))

    def test_getMessageStatus(self):
        print('testing getMessage Status function')
        self.assertTrue(self.bot_client.get_message_client().get_msg_status(self.messageId))

    def test_getSupportedAttachmentTypes(self):
        print('testing getAttachmentType function')
        self.assertTrue(self.bot_client.get_message_client().get_supported_attachment_types())


if __name__ == '__main__':
    unittest.main()
