import requests
import json
import logging
from ..DataFeedEventService import DataFeedEventService
from .apiClient import APIClient
from ..exceptions.APIClientErrorException import APIClientErrorException
from ..exceptions.ForbiddenException import ForbiddenException
from ..exceptions.ServerErrorException import ServerErrorException
from ..exceptions.UnauthorizedException import UnauthorizedException
# logging.basicConfig(filename='logs/example.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
# logging.getLogger("urllib3").setLevel(logging.WARNING)

#child class of APIClient --> Extends error handling functionality
#UserClient class contains a series of functions corresponding to all messaging
#endpoints on the REST API.
class UserClient(APIClient):

    def __init__(self, botClient):
        self.botClient = botClient
        self.config = botClient.getSymConfig()
        self.auth = botClient.getSymAuth()

    def getUsersV3(self, usersArray, local=False):
        logging.debug('UserClient/getUsersV3()')
        headers = {'sessionToken' : self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v3/users'
        usersArray = ','.join(map(str,usersArray))
        params = {'uid': usersArray, 'local': local}
        response = requests.get(url, headers=headers, params=params)
        print(response.url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response)
            except UnauthorizedException:
                self.getUsersV3(usersArray)

    def getUsersV2(self, usersArray, local=False):
        logging.debug('UserClient/getUsersV2()')
        headers = {'sessionToken' : self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v2/user'
        usersArray = ','.join(map(str,usersArray))
        params = {'uid': usersArray, 'local': local}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response)
            except UnauthorizedException:
                self.getUsersV2(usersArray)

    def searchUsers(self, query, local=False, skip=0, limit=50):
        logging.debug('UserClient/searchUsers()')
        headers = {'sessionToken' : self.auth.sessionToken}
        url = self.config.data['podHost']+'/pod/v1/user/search'
        params = {'local': local, 'skip': skip, 'limit': limit}
        data = {'query':query}
        response = requests.post(url, headers=headers, params=params, json=data)
        print(response.url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(response.status_code)
            try:
                super().handleError(response)
            except UnauthorizedException:
                self.searchUsers(query, local, skip, limit)
