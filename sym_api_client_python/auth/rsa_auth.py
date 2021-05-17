import json
import requests
import datetime
import time
import logging
from .auth_endpoint_constants import auth_endpoint_constants
from jose import jwt
from ..clients.api_client import APIClient
from ..exceptions.MaxRetryException import MaxRetryException

class SymBotRSAAuth(APIClient):
    """Class for RSA authentication"""

    def __init__(self, config):
        """
        Set up proxy information if configuration contains proxyURL
        :param config: Object contains all RSA configurations
        """
        self.config = config
        self.last_auth_time = 0
        self.auth_retries = 0
        self.session_token = None
        self.key_manager_token = None
        self.auth_session = requests.Session()
        self.key_manager_auth_session = requests.Session()

        self.auth_session.proxies.update(self.config.data['podProxyRequestObject'])
        self.key_manager_auth_session.proxies.update(self.config.data['keyManagerProxyRequestObject'])

        if self.config.data['truststorePath']:
            logging.debug('truststore being added to requests library')
            self.auth_session.verify = self.config.data['truststorePath']
            self.key_manager_auth_session.verify = self.config.data['truststorePath']

    def get_session_token(self):
        """Return the session token"""
        return self.session_token

    def get_key_manager_token(self):
        """Return the key manager token"""
        return self.key_manager_token

    def authenticate(self):
        """
        Get the session and key manager token
        """
        logging.debug('RSA Auth/authenticate()')
        try:
            if (self.last_auth_time == 0) or \
                    (int(round(time.time() * 1000) - self.last_auth_time >= auth_endpoint_constants['WAIT_TIME'])):
                logging.debug('RSA Auth/authenticate() --> needed to authenticate')

                self.last_auth_time = int(round(time.time() * 1000))
                self.session_authenticate()
                self.key_manager_authenticate()

            else:
                logging.debug('Retry authentication in 30 seconds.')
                time.sleep(auth_endpoint_constants['TIMEOUT'])
                self.authenticate()
        except MaxRetryException as e:
            logging.exception(e)
            raise MaxRetryException

    def create_jwt(self):
        """
        Create a jwt token with payload dictionary. Encode with
        RSA private key using RS512 algorithm

        :return: A jwt token valid for < 290 seconds
        """
        logging.debug('RSA_auth/getJWT() function started')
        with open(self.config.data['botRSAPath'], 'r') as f:
            content = f.readlines()
            private_key = ''.join(content)
            expiration_date = int(datetime.datetime.now(datetime.timezone.utc)
                                  .timestamp() + (5*58))
            payload = {
                'sub': self.config.data['botUsername'],
                'exp': expiration_date
            }
            encoded = jwt.encode(payload, private_key, algorithm='RS512')
            return encoded

    def session_authenticate(self):
        """
        Get the session token by calling API using jwt token
        """
        logging.debug('RSA_auth/get_session_token() function started')
        data = {
            'token': self.create_jwt()
        }
        url = self.config.data['sessionAuthUrl']+'/login/pubkey/authenticate'
        response = self.auth_session.post(url, json=data)

        if response.status_code != 200:
            self.auth_retries += 1
            if self.auth_retries > auth_endpoint_constants['MAX_RSA_RETRY']:
                # raise UnauthorizedException('max auth retry limit: {}'.format(response.__dict__))
                raise MaxRetryException('bot failed to authenticate more than 5 times.')
            else:
                logging.debug('RSA_auth/get_session_token() function failed: {}'.format(
                    response.status_code)
                )
                time.sleep(auth_endpoint_constants['TIMEOUT'])
                self.session_authenticate()
        else:
            data = json.loads(response.text)
            logging.debug('RSA/session token success')
            self.session_token = data['token']
            self.auth_retries = 0


    def key_manager_authenticate(self):
        """
        Get the key manager token by calling API using jwt token
        """
        logging.debug('RSA_auth/get_keyauth()')
        data = {
            'token': self.create_jwt()
        }
        url = self.config.data['keyAuthUrl']+'/relay/pubkey/authenticate'
        response = self.key_manager_auth_session.post(url, json=data)

        if response.status_code != 200:
            self.auth_retries += 1
            if self.auth_retries > auth_endpoint_constants['MAX_RSA_RETRY']:

                raise MaxRetryException('bot failed to authenticate more than 5 times.')
            else:
                logging.debug('RSA_auth/get_key_manager_authenticate() function failed: {}'.format(
                    response.status_code)
                )
                time.sleep(auth_endpoint_constants['TIMEOUT'])
                self.key_manager_authenticate()
        else:
            data = json.loads(response.text)
            logging.debug('RSA/key manager token success')
            self.key_manager_token = data['token']
            self.auth_retries = 0
