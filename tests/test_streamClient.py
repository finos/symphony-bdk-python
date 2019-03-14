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
#TestStreams class extends unittest class
#setUp functions executes before every test function runs --> grabs necessary data to run each client test
#streamId is hard coded --> replace with your own streamId to test if necessary
#execute by navigating to tests folder --> type 'python3 -m unittest discover' in commandline to execute each test
#comment any function that you no longer wish to test
class TestStreams(unittest.TestCase):

    # run before each test function
    def setUp(self):
        logging.debug('hi')
        #RSA Auth flow:
        configure = SymConfig('sym_api_client_python/resources/rsa_config.json')
        configure.load_rsa_config()
        auth = SymBotRSAAuth(configure)
        auth.authenticate()
        #initialize SymBotClient with auth and configure objects
        self.botClient = SymBotClient(auth, configure)
        self.streamId = 'GVYRWwxRnEI7xde31EQz63___prrBEtgdA'

    #always passes
    # def test_facts(self):
    #     self.assertEqual(1,1)
    #pass
    # def test_createIM(self):
    #     print('testing CreateIm function')
    #     self.assertTrue(self.bot_client.stream_client.create_im(self.user))

    #pass but will fail if you pass data thats already been used like name and description
    # def test_createRoom(self):
    #     print('testing create_room function')
    #     self.assertTrue(self.bot_client.stream_client.create_room())

    #pass: make sure that bot or user that is making update_room call is owner of room
    # def test_updateRoom(self):
    #     print('testing update_room function')
    #     roomId = 'gISNKeh49K344vkNggIMZn___puUpO5IdA'
    #     self.assertTrue(self.bot_client.stream_client.update_room(roomId))

    #pass
    # def test_roomInfo(self):
    #     print('testing roomInfo function')
    #     roomId = 'gISNKeh49K344vkNggIMZn___puUpO5IdA'
    #     self.assertTrue(self.bot_client.stream_client.roomInfo(roomId))

    #pass
    # def test_activateRoom(self):
    #     print('testing activate_room function')
    #     active = False
    #     roomId = 'gISNKeh49K344vkNggIMZn___puUpO5IdA'
    #     self.assertTrue(self.bot_client.stream_client.activate_room(roomId, active))

    #pass
    # def test_getRoomMembers(self):
    #     roomId = '5bxYnSD_ojes-inlYX0NeH___ptxUZqSdA'
    #     self.assertTrue(self.bot_client.stream_client.get_room_members(roomId))

    # pass
    # def test_addMember(self):
    #     print('testing addmember function')
    #     roomId = 'NyLNtKZwstZLapBgzR1Nqn___pt1T1EpdA'
    #     userId = '344147139494862'
    #     self.assertTrue(self.bot_client.stream_client.add_member_to_room(roomId, userId))

    #pass
    # def test_shareRoom(self):
    #     print('testing share_room function')
    #     roomId = 'NqlZTCH2C-JCZ5dRKbcFMX___pt1wct2dA'
    #     self.assertTrue(self.bot_client.stream_client.share_room(roomId))

    #pass
    # def test_removeMemberFromRoom(self):
    #     print('testing remove Member function')
    #     roomId = 'NqlZTCH2C-JCZ5dRKbcFMX___pt1wct2dA'
    #     userId = '344147139494862'
    #     self.assertTrue(self.bot_client.stream_client.remove_member_from_room(roomId, userId))

    #pass
    # def test_promoteUserToOwner(self):
    #     print('testing promote owner function')
    #     roomId = 'NyLNtKZwstZLapBgzR1Nqn___pt1T1EpdA'
    #     userId = '344147139494862'
    #     self.assertTrue(self.bot_client.stream_client.promote_user_to_owner(roomId, userId))

    #pass
    # def test_demoteUserFromOwner(self):
    #     print('testing demote owner function')
    #     roomId = 'NyLNtKZwstZLapBgzR1Nqn___pt1T1EpdA'
    #     userId = '344147139494862'
    #     self.assertTrue(self.bot_client.stream_client.demote_user_from_owner(roomId, userId))

    #pass
    # def test_searchRooms(self):
    #     print('testing roomSearch function')
    #     self.assertTrue(self.bot_client.stream_client.search_rooms())

    #pass
    # def test_getUserStreams(self):
    #     print('testing listUserStreams fucntion')
    #     self.assertTrue(self.bot_client.stream_client.get_user_streams())

    #pass
    # def test_getRoomInfo(self):
    #     print('testing streamInfo function')
    #     roomId = 'NyLNtKZwstZLapBgzR1Nqn___pt1T1EpdA'
    #     self.assertTrue(self.bot_client.stream_client.get_room_info(roomId))

    #pass
    # def test_streamInfo(self):
    #     print('testing streamInfo V2 function')
    #     roomId = 'NyLNtKZwstZLapBgzR1Nqn___pt1T1EpdA'
    #     self.assertTrue(self.bot_client.stream_client.streamInfo(roomId))

    #pass
    # def test_listStreamsEnterprise(self):
    #     print('testing list streams enterprise function')
    #     self.assertTrue(self.bot_client.stream_client.list_streams_enterprise())

    #DOESNOTPASS
    # def test_listStreamsEnterpriseV2(self):
    #     print('testing list streamsV2 enterprise function')
    #     self.assertTrue(self.bot_client.stream_client.list_streams_enterprise_v2())

    #DOESNOTPASS --> 405: verify if endpoint is still live
    # def test_getStreamMembers(self):
    #     print('testing getstreamMembers function')
    #     self.assertTrue(self.bot_client.stream_client.get_stream_members(self.streamId))

# if __name__ == '__main__':
#     unittest.main()
