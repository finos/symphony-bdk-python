import requests
import json
import logging
from .apiClient import APIClient
from ..exceptions.APIClientErrorException import APIClientErrorException
from ..exceptions.ForbiddenException import ForbiddenException
from ..exceptions.ServerErrorException import ServerErrorException
from ..exceptions.UnauthorizedException import UnauthorizedException
# logging.basicConfig(filename='logs/example.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
# logging.getLogger("urllib3").setLevel(logging.WARNING)
#child class of APIClient --> Extends error handling functionality
#MessageClient class contains a series of functions corresponding to all messaging
#endpoints on the REST API.
class MessageClient(APIClient):

    def __init__(self, botClient):
        self.botClient = botClient
        self.config = botClient.getSymConfig()
        self.auth = botClient.getSymAuth()

    def getMessages(self, streamId, since):
        logging.debug('MessageClient/getMessages()')
        headers = {'sessionToken':self.auth.sessionToken, 'keyManagerToken': self.auth.keyAuthToken}
        url = self.config.data['agentHost']+'/agent/v4/stream/{0}/message?since={1}'.format(streamId, since)
        response = requests.get(url, headers=headers)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, botClient)
            except UnauthorizedException:
                getMessages(streamId, since)

    def createMessage(self, streamId, outBoundMessage):
        logging.debug('MessageClient/createMessage()')
        url = self.config.data['agentHost']+'/agent/v4/stream/{0}/message/create'.format(streamId)
        headers = {'sessionToken':self.auth.sessionToken, 'keyManagerToken': self.auth.keyAuthToken}
        response = requests.post(url, files=outBoundMessage, headers=headers)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response)
            except UnauthorizedException:
                self.createMessage(streamId, outBoundMessage)

    def getAttachments(self, streamId, messageId, fileId):
        logging.debug('MessageClient/getAttachments()')
        headers = {'sessionToken':self.auth.sessionToken, 'keyManagerToken': self.auth.keyAuthToken}
        url = self.config.data['agentHost']+'/agent/v1/stream/{0}/attachment?messageId={1}&fileId={2}'.format(streamId, messageId, fileId)
        response = requests.get(url, headers=headers)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response)
            except UnauthorizedException:
                self.getAttachments(streamId, messageId, field)

    #go on admin clients --> Contains sample data just for example's sake
    def importMessage(self):
        logging.debug('MessageClient/importMessage()')
        headers = {'sessionToken':self.auth.sessionToken, 'keyManagerToken': self.auth.keyAuthToken}
        url = self.config.data['agentHost']+'/agent/v4/message/import'
        payload = {
            "message": "<messageML>Imported message</messageML>",
            "format": "MESSAGEML",
            "intendedMessageTimestamp": 1433045622000,
            "intendedMessageFromUserId": 7215545057281,
            "originatingSystemId": "",
            "originalMessageId": "",
            "streamId": ""
        }
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response)
            except UnauthorizedException:
                self.importMessage()

    #go on admin clients
    def suppressMessage(self, id):
        logging.debug('MessageClient/suppressMessage()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v1/admin/messagesuppression/{0}/suppress'.format(id)
        response = requests.post(url, headers=headers)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response)
            except UnauthorizedException:
                self.suppressMessage(id)


    def postMessageSearch(self):
        logging.debug('MessageClient/postMessageSearch()')
        headers = {'sessionToken':self.auth.sessionToken, 'keyManagerToken': self.auth.keyAuthToken}
        url = self.config.data['agentHost']+'/agent/v1/message/search'
        payload = {'hashtag':'reed'}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response)
            except UnauthorizedException:
                self.postMessageSearch(id)

    #contains sample query for example
    def getMessageSearch(self):
        logging.debug('MessageClient/getMessageSearch()')
        headers = {'sessionToken':self.auth.sessionToken, 'keyManagerToken': self.auth.keyAuthToken}
        url = self.config.data['agentHost']+'/agent/v1/message/search'
        query = {'query': 'hashtag:reed'}
        response = requests.get(url, headers=headers, params=query)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response)
            except UnauthorizedException:
                self.getMessageSearch(id)

    def getMessageStatus(self, messageId):
        logging.debug('MessageClient/getMessageStatus()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v1/message/{0}/status'.format(messageId)
        response = requests.get(url, headers=headers)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response)
            except UnauthorizedException:
                self.getAttachments(messageId)

    def getAttachmentTypes(self):
        logging.debug('MessageClient/getAttachmentTypes()')
        headers = {'sessionToken':self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v1/files/allowedTypes'
        response = requests.get(url, headers=headers)
        if response.status_code == 204:
            result = []
            return result
        elif response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response)
            except UnauthorizedException:
                self.getAttachmentTypes()
