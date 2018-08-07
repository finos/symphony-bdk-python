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
        self.config = self.botClient.getSymConfig()
        if self.config.data['proxyURL']:
            self.proxies = {"http": self.config.data['proxyURL']}
        else:
            self.proxies = {}

    def getUserFromUsername(self, userName):
        logging.debug('UserClient/getUserFromUserName()')
        headers = {'sessionToken': self.botClient.getSymAuth().getSessionToken()}
        url = self.config.data['podHost']+'/pod/v2/user'
        params = {'username': userName}
        response = requests.get(url, headers=headers, params=params, proxies=self.proxies)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, self.botClient)
            except UnauthorizedException:
                self.getUserFromUserName(userName)

    def getUserFromEmail(self, email, local=False):
        logging.debug('UserClient/getUserFromEmail()')
        headers = {'sessionToken': self.botClient.getSymAuth().getSessionToken()}
        url = self.config.data['podHost']+'/pod/v2/user'
        params = {'email': email, 'local':local}
        response = requests.get(url, headers=headers, params=params, proxies=self.proxies)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, self.botClient)
            except UnauthorizedException:
                self.getUserFromEmail(email)

    def getUserFromId(self, id, local=False):
        logging.debug('UserClient/getUserFromId')
        headers = {'sessionToken': self.botClient.getSymAuth().getSessionToken()}
        url = self.config.data['podHost']+'/pod/v2/user'
        params = {'uid': id, 'local':local}
        response = requests.get(url, headers=headers, params=params, proxies=self.proxies)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, self.botClient)
            except UnauthorizedException:
                self.getUserFromId(id)


    def getUsersFromIdList(self, idList, local=False):
        logging.debug('UserClient/getUsersFromIdList()')
        headers = {'sessionToken': self.botClient.getSymAuth().getSessionToken()}
        url = self.config.data['podHost']+'/pod/v3/users'
        usersArray = ','.join(map(str,idList))
        params = {'uid': usersArray, 'local': local}
        response = requests.get(url, headers=headers, params=params, proxies=self.proxies)
        print(response.url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, self.botClient)
            except UnauthorizedException:
                self.getUsersFromIdList(idList)

    def getUsersFromEmailList(self, emailList, local=False):
        logging.debug('UserClient/getUsersFromEmailList()')
        headers = {'sessionToken': self.botClient.getSymAuth().getSessionToken()}
        url = self.config.data['podHost']+'/pod/v3/users'
        usersArray = ','.join(map(str,emailList))
        print(usersArray)
        params = {'email': usersArray, 'local': local}
        response = requests.get(url, headers=headers, params=params, proxies=self.proxies)
        print(response.url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handleError(response, self.botClient)
            except UnauthorizedException:
                self.getUsersFromIdList(idList)

    def searchUsers(self, query, local=False, skip=0, limit=50, filter={}):
        logging.debug('UserClient/searchUsers()')
        headers = {'sessionToken': self.botClient.getSymAuth().getSessionToken()}
        url = self.config.data['podHost']+'/pod/v1/user/search'
        params = {'local': local, 'skip': skip, 'limit': limit}
        data = {'query':query, 'filters': filter}
        response = requests.post(url, headers=headers, params=params, json=data, proxies=self.proxies)
        print(response.url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(response.status_code)
            try:
                super().handleError(response, self.botClient)
            except UnauthorizedException:
                self.searchUsers(query, local, skip, limit)
