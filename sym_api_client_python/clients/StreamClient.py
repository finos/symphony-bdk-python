import requests
import json
import logging
from .apiClient import APIClient
from ..exceptions.APIClientErrorException import APIClientErrorException
from ..exceptions.ServerErrorException import ServerErrorException
from ..exceptions.UnauthorizedException import UnauthorizedException
from ..exceptions.ForbiddenException import ForbiddenException
# logging.basicConfig(filename='logs/example.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
# logging.getLogger("urllib3").setLevel(logging.WARNING)

#child class of APIClient --> Extends error handling functionality
#StreamClient class contains a series of functions corresponding to all stream
#endpoints on the REST API.
class StreamClient(APIClient):

    def __init__(self, botClient):
        self.botClient = botClient
        self.config = botClient.getSymConfig()
        self.auth = botClient.getSymAuth()

    def createIM(self, usersArray):
        logging.debug('StreamClient/createIM()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v1/im/create'
        response = requests.post(url, json=usersArray, headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.createIM(usersArray)

    def createIMAdmin(self, usersArray):
        logging.debug('StreamClient/createIMAdmin()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v1/admin/im/create'
        response = requests.post(url, json=usersArray, headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.createIMAdmin(usersArray)


    #contains sample data for example's sake
    def createRoom(self):
        logging.debug('StreamClient/createRoom()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v3/room/create'
        data = {"name": "butlahsroom",
                "description": "meant for testing with butler"}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.createRoom()

    #contains example data dictionary for example sake
    def updateRoom(self, roomId):
        logging.debug('StreamClient/updateRoom()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v3/room/{0}/update'.format(roomId)
        data = {"name":"updatedRoomName"}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.updateRoom()

    def roomInfo(self, roomId):
        logging.debug('StreamClient/roomInfo()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v3/room/{0}/info'.format(roomId)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.roomInfo()


    def activateRoom(self, roomId, active):
        logging.debug('StreamClient/activateRoom()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v1/room/{0}/setActive?active={1}'.format(roomId, active)
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.activateRoom()

    def getRoomMembers(self,roomId):
        logging.debug('StreamClient/getRoomMembers()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v2/room/{0}/membership/list'.format(roomId)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.getRoomMembers()


    def addMember(self, roomId, userId):
        logging.debug('StreamClient/addMember()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v1/room/{0}/membership/add'.format(roomId)
        data = {'id': userId}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.addMember(roomId, userId)

    #contains sample data dictionary for example --> see documentation for further detail
    def shareRoom(self, roomId):
        logging.debug('StreamClient/shareRoom()')
        headers = {'sessionToken':self.auth.sessionToken, 'keyManagerToken': self.auth.keyAuthToken}
        url = self.config.data['agentHost']+'/agent/v3/stream/{0}/share'.format(roomId)
        data = {
        "type": "com.symphony.sharing.article",
        "content":{
        "articleId":"tsla",
        "title": "The Secrets Out: Tesla Enters China and Is Winning",
        "description": "Check this out",
        "publisher": "Capital Market Laboratories",
        "thumbnailUrl": "http://www.cmlviz.com/cmld3b/images/tesla-supercharger-stop.jpg",
        "author": "OPHIRGOTTLIEB",
        "articleUrl": "http://ophirgottlieb.tumblr.com/post/146623530819/the-secrets-out-tesla-enters-china-and-is",
        "summary": "Tesla Motors Inc. (NASDAQ:TSLA) has a CEO more famous than the firm itself, perhaps. Elon Musk has made some bold predictions, first stating that the firm would grow sales from 50,000 units in 2015 to 500,000 by 2020 powered by the less expensive Model 3 and the massive manufacturing capability of the Gigafactory.",
        "appId": "ticker",
        "appName": "Market Data Demo",
        "appIconUrl": "https://apps-dev.symphony.com/ticker/assets/images/logo.png"
            }
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.shareRoom(roomId, userId)


    def removeMember(self, roomId, userId):
            logging.debug('StreamClient/removeMember()')
            headers = {'sessionToken':self.auth.sessionToken}
            url = self.config.data['podHost']+'/pod/v1/room/{0}/membership/remove'.format(roomId)
            data = {'id': userId}
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                try:
                    super().handleError(response, botClient)
                except UnauthorizedException:
                    self.removeMember(roomId, userId)


    def promoteOwner(self, roomId, userId):
        logging.debug('StreamClient/promoteOwner()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v1/room/{0}/membership/promoteOwner'.format(roomId)
        data = {'id': userId}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.promoteOwner(roomId, userId)

    def demoteOwner(self, roomId, userId):
        logging.debug('StreamClient/demoteOwner()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v1/room/{0}/membership/demoteOwner'.format(roomId)
        data = {'id': userId}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.demoteOwner(roomId, userId)

    def roomSearch(self, skip=0, limit=50):
        logging.debug('StreamClient/roomSearch()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v3/room/search'
        params = {'skip':skip, 'limit':limit}
        data = {'query': 'butlahsroom'}
        response = requests.post(url, headers=headers, params=params, json=data)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.roomSearch(roomId, userId)

    def listUserStreams(self, skip=0, limit=50):
        logging.debug('StreamClient/listUserStreams()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v1/streams/list'
        data = {"streamTypes": [
                    {"type": "IM"},
                    {"type": "MIM"},
                    {"type": "ROOM"},
                    {"type": "POST"}
                  ],
                  "includeInactiveStreams": True
                }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.listUserStreams()

    def streamInfo(self, streamId):
        logging.debug('StreamClient/streamInfo()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v1/streams/{0}/info'.format(streamId)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.streamInfo()

    def streamInfoV2(self, streamId):
        logging.debug('StreamClient/streamInfoV2()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v2/streams/{0}/info'.format(streamId)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.streamInfoV2()

    def listStreamsEnterprise(self,skip=0, limit=50):
        logging.debug('StreamClient/listStreamsEnterprise()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v1/admin/streams/list'
        params = {'skip':skip, 'limit':limit}
        data = {
              "streamTypes": [{"type": "ROOM"}],
              "scope": "EXTERNAL",
              "origin": "EXTERNAL",
              "privacy": "PRIVATE",
              "status": "ACTIVE",
              "startDate": 1481575056047,
              "endDate": 1483038089833
            }
        response = requests.post(url, headers=headers, params=params, json=data)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                self.listStreamsEnterprise()


    def listStreamsEnterpriseV2(self,skip=0, limit=50):
        logging.debug('StreamClient/listStreamsEnterpriseV2()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v2/admin/streams/list'
        params = {'skip':skip, 'limit':limit}
        data = {
              "streamTypes": [{"type": "ROOM"}],
              "scope": "EXTERNAL",
              "origin": "EXTERNAL",
              "privacy": "PRIVATE",
              "status": "ACTIVE",
              "startDate": 1481575056047,
              "endDate": 1483038089833
            }
        response = requests.post(url, headers=headers, params=params, json=data)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response)
            except UnauthorizedException:
                self.listStreamsEnterpriseV2()


    def getStreamMembers(self,streamId, skip=0, limit=100):
        logging.debug('StreamClient/getStreamMembers()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v1/admin/stream/{0}/membership/list'.format(streamId)
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response)
            except UnauthorizedException:
                self.getstreamMembers(streamId)
