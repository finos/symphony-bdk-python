import json
import requests
import logging
from ..clients.apiClient import APIClient
from ..exceptions.UnauthorizedException import UnauthorizedException
# logging.basicConfig(filename='logs/example.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
# logging.getLogger("urllib3").setLevel(logging.WARNING)

class Auth():
    #initialize Auth object with config object and empty strings representing auth tokens
    def __init__(self, config):
        self.config = config
        self.sessionToken = ''
        self.keyAuthToken = ''
    #if sessionToken or keyAuthToken are empty --> call auth endpoints below
    def authenticate(self):
        if not(self.sessionToken or self.keyAuthToken):
            logging.debug('Auth/authenticate() --> needed to authenticate')
            self.sessionToken = self.get_session_token()
            self.keyAuthToken = self.get_keyauth()
        else:
            logging.debug('Auth/authenticate() --> did not need to authenticate')

    #raw auth api call to retrieve session token
    #pass in certificates from config object using requests library built in cert parameter
    def get_session_token(self):
        logging.debug('Auth/get_session_token()')
        response = requests.post(self.config.data['sessionAuthUrl']+'/sessionauth/v1/authenticate', cert=(self.config.data['symphonyCertificate'], self.config.data['symphonyKey']))
        if response.status_code == 200:
            data = json.loads(response.text)
            return data['token']
        else:
            logging.debug('Auth/get_session_token() failed: {}'.format(response.status_code))
            super().handleError(response)

    #raw auth api call to retrieve key manager token
    #pass in certificates from config object using requests library built in cert parameter
    def get_keyauth(self):
        logging.debug('Auth/get_keyauth()')
        response = requests.post(self.config.data['keyAuthUrl']+'/keyauth/v1/authenticate', cert=(self.config.data['symphonyCertificate'], self.config.data['symphonyKey']))
        if response.status_code == 200:
            data = json.loads(response.text)
            return data['token']
        else:
            logging.debug('Auth/get_keyauth() failed: {}'.format(response.status_code))
            super().handleError(response)
