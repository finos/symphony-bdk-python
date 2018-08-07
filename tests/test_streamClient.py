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
        configure.loadFromRSA()
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
    #     self.assertTrue(self.botClient.streamClient.createIM(self.user))

    #pass but will fail if you pass data thats already been used like name and description
    # def test_createRoom(self):
    #     print('testing createRoom function')
    #     self.assertTrue(self.botClient.streamClient.createRoom())

    #pass: make sure that bot or user that is making updateRoom call is owner of room
    # def test_updateRoom(self):
    #     print('testing updateRoom function')
    #     roomId = 'gISNKeh49K344vkNggIMZn___puUpO5IdA'
    #     self.assertTrue(self.botClient.streamClient.updateRoom(roomId))

    #pass
    # def test_roomInfo(self):
    #     print('testing roomInfo function')
    #     roomId = 'gISNKeh49K344vkNggIMZn___puUpO5IdA'
    #     self.assertTrue(self.botClient.streamClient.roomInfo(roomId))

    #pass
    # def test_activateRoom(self):
    #     print('testing activateRoom function')
    #     active = False
    #     roomId = 'gISNKeh49K344vkNggIMZn___puUpO5IdA'
    #     self.assertTrue(self.botClient.streamClient.activateRoom(roomId, active))

    #pass
    # def test_getRoomMembers(self):
    #     roomId = '5bxYnSD_ojes-inlYX0NeH___ptxUZqSdA'
    #     self.assertTrue(self.botClient.streamClient.getRoomMembers(roomId))

    # pass
    # def test_addMember(self):
    #     print('testing addmember function')
    #     roomId = 'NyLNtKZwstZLapBgzR1Nqn___pt1T1EpdA'
    #     userId = '344147139494862'
    #     self.assertTrue(self.botClient.streamClient.addMemberToRoom(roomId, userId))

    #pass
    # def test_shareRoom(self):
    #     print('testing shareRoom function')
    #     roomId = 'NqlZTCH2C-JCZ5dRKbcFMX___pt1wct2dA'
    #     self.assertTrue(self.botClient.streamClient.shareRoom(roomId))

    #pass
    # def test_removeMemberFromRoom(self):
    #     print('testing remove Member function')
    #     roomId = 'NqlZTCH2C-JCZ5dRKbcFMX___pt1wct2dA'
    #     userId = '344147139494862'
    #     self.assertTrue(self.botClient.streamClient.removeMemberFromRoom(roomId, userId))

    #pass
    # def test_promoteUserToOwner(self):
    #     print('testing promote owner function')
    #     roomId = 'NyLNtKZwstZLapBgzR1Nqn___pt1T1EpdA'
    #     userId = '344147139494862'
    #     self.assertTrue(self.botClient.streamClient.promoteUserToOwner(roomId, userId))

    #pass
    # def test_demoteUserFromOwner(self):
    #     print('testing demote owner function')
    #     roomId = 'NyLNtKZwstZLapBgzR1Nqn___pt1T1EpdA'
    #     userId = '344147139494862'
    #     self.assertTrue(self.botClient.streamClient.demoteUserFromOwner(roomId, userId))

    #pass
    # def test_searchRooms(self):
    #     print('testing roomSearch function')
    #     self.assertTrue(self.botClient.streamClient.searchRooms())

    #pass
    # def test_getUserStreams(self):
    #     print('testing listUserStreams fucntion')
    #     self.assertTrue(self.botClient.streamClient.getUserStreams())

    #pass
    # def test_getRoomInfo(self):
    #     print('testing streamInfo function')
    #     roomId = 'NyLNtKZwstZLapBgzR1Nqn___pt1T1EpdA'
    #     self.assertTrue(self.botClient.streamClient.getRoomInfo(roomId))

    #pass
    # def test_streamInfo(self):
    #     print('testing streamInfo V2 function')
    #     roomId = 'NyLNtKZwstZLapBgzR1Nqn___pt1T1EpdA'
    #     self.assertTrue(self.botClient.streamClient.streamInfo(roomId))

    #pass
    # def test_listStreamsEnterprise(self):
    #     print('testing list streams enterprise function')
    #     self.assertTrue(self.botClient.streamClient.listStreamsEnterprise())

    #DOESNOTPASS
    # def test_listStreamsEnterpriseV2(self):
    #     print('testing list streamsV2 enterprise function')
    #     self.assertTrue(self.botClient.streamClient.listStreamsEnterpriseV2())

    #DOESNOTPASS --> 405: verify if endpoint is still live
    # def test_getStreamMembers(self):
    #     print('testing getstreamMembers function')
    #     self.assertTrue(self.botClient.streamClient.getStreamMembers(self.streamId))

# if __name__ == '__main__':
#     unittest.main()
