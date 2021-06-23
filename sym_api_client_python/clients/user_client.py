import logging

from .api_client import APIClient


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

    def get_user_from_user_name(self, user_name):
        logging.debug('UserClient/get_user_from_user_name()')
        url = '/pod/v2/user'
        params = {'username': user_name}
        return self.bot_client.execute_rest_call('GET', url, params=params)

    def get_user_from_email(self, email, local=False):
        logging.debug('UserClient/get_user_from_email()')
        url = '/pod/v2/user'
        params = {'email': email, 'local':local}
        return self.bot_client.execute_rest_call('GET', url, params=params)

    def get_user_from_id(self, user_id, local=False):
        logging.debug('UserClient/get_user_from_id()')
        url = '/pod/v2/user'
        params = {'uid': user_id, 'local':local}
        return self.bot_client.execute_rest_call('GET', url, params=params)

    def get_users_from_id_list(self, user_id_list, local=False):
        logging.debug('UserClient/get_users_from_id_list()')
        url = '/pod/v3/users'
        users_array = ','.join(map(str, user_id_list))
        params = {'uid': users_array, 'local': local}
        return self.bot_client.execute_rest_call('GET', url, params=params)

    def get_users_from_email_list(self, email_list, local=False):
        logging.debug('UserClient/get_users_from_email_list()')
        url = '/pod/v3/users'
        usersArray = ','.join(map(str, email_list))
        params = {'email': usersArray, 'local': local}
        return self.bot_client.execute_rest_call('GET', url, params=params)

    def search_users(self, query, local=False, skip=0, limit=50, filters={}):
        logging.debug('UserClient/search_users()')
        url = '/pod/v1/user/search'
        params = {'local': local, 'skip': skip, 'limit': limit}
        data = {'query':query, 'filters': filters}
        return self.bot_client.execute_rest_call('POST', url, params=params, json=data)

    def get_session_user(self):
        logging.debug('UserClient/get_session_user()')
        url = '/pod/v2/sessioninfo'
        return self.bot_client.execute_rest_call('GET', url)
