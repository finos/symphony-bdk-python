import json
import logging
import time
import requests
from .auth_endpoint_constants import auth_endpoint_constants
from ..clients.api_client import APIClient
from requests_pkcs12 import Pkcs12Adapter
from ..exceptions.UnauthorizedException import UnauthorizedException
from ..exceptions.MaxRetryException import MaxRetryException


class Auth(APIClient):
    """Class for certificate authentication"""

    def __init__(self, config):
        """
        Set up proxy information if configuration contains proxyURL
        :param config: Object contains all certificate configurations
        """
        self.config = config
        self.agentConfig = config
        self.last_auth_time = 0
        self.auth_retries = 0
        self.session_token = None
        self.key_manager_token = None
        self.auth_session = requests.Session()
        self.key_manager_auth_session = requests.Session()

        # proxy infomation set in config loader, set to empty object if there is no proxy set in config.json
        self.auth_session.proxies.update(self.config.data['podProxyRequestObject'])
        self.key_manager_auth_session.proxies.update(self.config.data['keyManagerProxyRequestObject'])

        if self.config.data['truststorePath']:
            logging.debug('truststore being added to requests library')
            self.auth_session.verify = self.config.data['truststorePath']
            self.key_manager_auth_session.verify = self.config.data['truststorePath']

        self.auth_session.mount(
            self.config.data['sessionAuthUrl'],
            Pkcs12Adapter(
                pkcs12_filename=self.config.data['p.12'],
                pkcs12_password=self.config.data['botCertPassword']
            ))
        self.auth_session.mount(
            self.config.data['keyAuthUrl'],
            Pkcs12Adapter(
                pkcs12_filename=self.config.data['p.12'],
                pkcs12_password=self.config.data['botCertPassword']
            ))

        self.key_manager_auth_session.mount(
            self.config.data['sessionAuthUrl'],
            Pkcs12Adapter(
                pkcs12_filename=self.config.data['p.12'],
                pkcs12_password=self.config.data['botCertPassword']
            ))
        self.key_manager_auth_session.mount(
            self.config.data['keyAuthUrl'],
            Pkcs12Adapter(
                pkcs12_filename=self.config.data['p.12'],
                pkcs12_password=self.config.data['botCertPassword']
            ))

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
        logging.debug('Auth/authenticate()')
        try:
            if (self.last_auth_time == 0) or \
                    (int(round(time.time() * 1000) - self.last_auth_time >= auth_endpoint_constants['WAIT_TIME'])):
                logging.debug('Auth/authenticate() --> needed to authenticate')

                self.last_auth_time = int(round(time.time() * 1000))
                self.session_authenticate()
                self.key_manager_authenticate()

            else:
                logging.debug('Retry authentication in 30 seconds.')
                time.sleep(auth_endpoint_constants['TIMEOUT'])
                self.authenticate()
        except:
            raise MaxRetryException('max auth retry limit')

    # Retrieve session token by calling the session token API
    # Certificates are passed in cert parameter
    def session_authenticate(self):
        """
        Get the session token by calling API, certificate data is
        passed in through Request Session object
        """
        logging.debug('Auth/get_session_token()')

        url = self.config.data['sessionAuthUrl'] + '/sessionauth/v1/authenticate'
        response = self.auth_session.post(url)

        if response.status_code != 200:
            self.auth_retries += 1
            if self.auth_retries > auth_endpoint_constants['MAX_AUTH_RETRY']:
                logging.debug('more than 5 times tried')
                raise UnauthorizedException('max auth retry limit: {}'.format(response.__dict__))
            else:
                logging.debug('Auth/get_session_token() function failed: {}'.format(
                    response.status_code)
                )
                time.sleep(auth_endpoint_constants['TIMEOUT'])
                self.session_authenticate()
        else:
            data = json.loads(response.text)
            logging.debug('Auth/session token success')
            self.session_token = data['token']
            self.auth_retries = 0

    def key_manager_authenticate(self):
        """
        Get the key manager token by calling API, certificate data is
        passed in through Request Session object
        """
        logging.debug('Auth/get_keyauth()')
        url = self.config.data['keyAuthUrl'] + '/keyauth/v1/authenticate'
        response = self.key_manager_auth_session.post(url)

        if response.status_code != 200:
            self.auth_retries += 1
            if self.auth_retries > auth_endpoint_constants['MAX_AUTH_RETRY']:
                raise UnauthorizedException('max auth retry limit: {}'.format(response.__dict__))
            else:
                logging.debug('Auth/get_key_manager_authenticate() function failed: {}'.format(
                    response.status_code)
                )
                time.sleep(auth_endpoint_constants['TIMEOUT'])
                self.key_manager_authenticate()
        else:
            data = json.loads(response.text)
            logging.debug('Auth/key manager token success')
            self.key_manager_token = data['token']
            self.auth_retries = 0
