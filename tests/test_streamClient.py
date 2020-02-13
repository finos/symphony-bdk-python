import json
import logging
import unittest

import requests

from sym_api_client_python.auth.auth import Auth
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.configure.configure import SymConfig
from sym_api_client_python.listeners.im_listener_test_imp import \
    IMListenerTestImp
from sym_api_client_python.listeners.room_listener_test_imp import \
    RoomListenerTestImp
from sym_api_client_python.loaders import load_from_env_var

logging.basicConfig(filename='sym_api_client_python/logs/example.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)
#TestStreams class extends unittest class
#setUp functions executes before every test function runs --> grabs necessary data to run each client test
#streamId is hard coded --> replace with your own streamId to test if necessary
#execute by navigating to tests folder --> type 'python3 -m unittest discover' in commandline to execute each test
#comment any function that you no longer wish to test
class TestStreams(unittest.TestCase):

    # run before each test function
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

        # Initialize SymBotClient with auth and configure objects
        self.bot_client = SymBotClient(self.auth, self.configure)
        self.streamId = 'qfC1jCKzQ0ELq96TMs58dX___o_kveOkdA'
        self.user_id = '349026222344902'

    #always passes
    # def test_facts(self):
    #     self.assertEqual(1,1)
    #pass
    def test_createIM(self):
        print('testing CreateIm function')
        self.assertTrue(self.bot_client.get_stream_client().create_im([self.user_id]))

    #pass but will fail if you pass data thats already been used like name and description
    def test_createRoom(self):
        print('testing create_room function')
        self.assertTrue(self.bot_client.get_stream_client().create_room())

    #pass: make sure that bot or user that is making update_room call is owner of room
    def test_updateRoom(self):
        print('testing update_room function')

        self.assertTrue(self.bot_client.get_stream_client().update_room(self.room_id))

    #pass
    def test_roomInfo(self):
        print('testing roomInfo function')

        self.assertTrue(self.bot_client.get_stream_client().get_room_info(self.streamId))

    #pass
    def test_activateRoom(self):
        print('testing activate_room function')
        active = False

        self.assertTrue(self.bot_client.get_stream_client().activate_room(self.streamId))

    #pass
    def test_getRoomMembers(self):

        self.assertTrue(self.bot_client.get_stream_client().get_room_members(self.streamId))

    #pass
    def test_addMember(self):
        print('testing addmember function')

        userId = '344147139494862'
        self.assertTrue(self.bot_client.get_stream_client().add_member_to_room(self.streamId, self.user_id))

    #pass
    def test_shareRoom(self):
        print('testing share_room function')

        self.assertTrue(self.bot_client.get_stream_client().share_room(self.stream_id))

    #pass
    def test_removeMemberFromRoom(self):
        print('testing remove Member function')

        userId = '344147139494862'
        self.assertTrue(self.bot_client.get_stream_client().remove_member_from_room(self.stream_id, self.user_id))

    #pass
    def test_promoteUserToOwner(self):
        print('testing promote owner function')

        userId = '344147139494862'
        self.assertTrue(self.bot_client.get_stream_client().promote_user_to_owner(self.stream_id, self.user_id))

    #pass
    def test_demoteUserFromOwner(self):
        print('testing demote owner function')

        userId = '344147139494862'
        self.assertTrue(self.bot_client.get_stream_client().demote_user_from_owner(self.stream_id, self.user_id))

    #pass
    def test_searchRooms(self):
        print('testing roomSearch function')
        self.assertTrue(self.bot_client.get_stream_client().search_rooms())

    #pass
    def test_getUserStreams(self):
        print('testing listUserStreams fucntion')
        self.assertTrue(self.bot_client.get_stream_client().get_user_streams())

    #pass
    def test_getRoomInfo(self):
        print('testing streamInfo function')

        self.assertTrue(self.bot_client.get_stream_client().get_room_info(self.room_id))

    #pass
    def test_streamInfo(self):
        print('testing streamInfo V2 function')

        self.assertTrue(self.bot_client.get_stream_client().streamInfo(self.room_id))

    #pass
    def test_listStreamsEnterprise(self):
        print('testing list streams enterprise function')
        self.assertTrue(self.bot_client.get_stream_client().list_streams_enterprise())

    #DOESNOTPASS
    def test_listStreamsEnterpriseV2(self):
        print('testing list streamsV2 enterprise function')
        self.assertTrue(self.bot_client.get_stream_client().list_streams_enterprise_v2())

    #DOESNOTPASS --> 405: verify if endpoint is still live
    def test_getStreamMembers(self):
        print('testing getstreamMembers function')
        self.assertTrue(self.bot_client.get_stream_client().get_stream_members(self.streamId))

# if __name__ == '__main__':
#     unittest.main()
