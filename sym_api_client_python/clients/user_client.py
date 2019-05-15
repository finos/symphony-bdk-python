import requests
import json
import logging
from .api_client import APIClient
from ..exceptions.UnauthorizedException import UnauthorizedException
# logging.basicConfig(filename='logs/example.log', format='%(asctime)s - %(
# name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
# logging.getLogger("urllib3").setLevel(logging.WARNING)

# child class of APIClient --> Extends error handling functionality
# UserClient class contains a series of functions corresponding to all
# messaging
# endpoints on the REST API.


class UserClient(APIClient):

    def __init__(self, bot_client):
        self.bot_client = bot_client
        self.config = self.bot_client.get_sym_config()
        self.pod_proxies = self.config.data['podProxyRequestObject']

    def get_user_from_user_name(self, user_name):
        logging.debug('UserClient/get_user_from_user_name()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost']+'/pod/v2/user'
        params = {'username': user_name}
        response = requests.get(
            url, headers=headers, params=params, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.get_user_from_user_name(user_name)

    def get_user_from_email(self, email, local=False):
        logging.debug('UserClient/get_user_from_email()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost']+'/pod/v2/user'
        params = {'email': email, 'local':local}
        response = requests.get(
            url, headers=headers, params=params, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.get_user_from_email(email)

    def get_user_from_id(self, user_id, local=False):
        logging.debug('UserClient/get_user_from_id')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost']+'/pod/v2/user'
        params = {'uid': user_id, 'local':local}
        response = requests.get(
            url, headers=headers, params=params, proxies=self.pod_proxies
        )
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.get_user_from_id(user_id)

    def get_users_from_id_list(self, user_id_list, local=False):
        logging.debug('UserClient/get_users_from_id_list()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost']+'/pod/v3/users'
        users_array = ','.join(map(str, user_id_list))
        params = {'uid': users_array, 'local': local}
        response = requests.get(
            url, headers=headers, params=params, proxies=self.pod_proxies
        )
        print(response.url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.get_users_from_id_list(id_list)

    def get_users_from_email_list(self, email_list, local=False):
        logging.debug('UserClient/get_users_from_email_list()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost']+'/pod/v3/users'
        usersArray = ','.join(map(str, email_list))
        print(usersArray)
        params = {'email': usersArray, 'local': local}
        response = requests.get(
            url, headers=headers, params=params, proxies=self.pod_proxies
        )
        print(response.url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.get_users_from_email_list(email_list)

    def search_users(self, query, local=False, skip=0, limit=50, filters={}):
        logging.debug('UserClient/search_users()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token()
        }
        url = self.config.data['podHost']+'/pod/v1/user/search'
        params = {'local': local, 'skip': skip, 'limit': limit}
        data = {'query':query, 'filters': filters}
        response = requests.post(
            url, headers=headers, params=params, json=data,
            proxies=self.pod_proxies
        )
        print(response.url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(response.status_code)
            try:
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                self.search_users(query, local, skip, limit)
