import json
import logging
import time
from requests import Session
from requests_pkcs12 import Pkcs12Adapter


class Auth:
    """Class for certificate authentication"""

    def __init__(self, config):
        """
        Set up proxy information if configuration contains proxyURL

        :param config: Object contains all certificate configurations
        """
        self.config = config
        self.last_auth_time = 0
        self.session_token = None
        self.key_manager_token = None
        if self.config.data['proxyURL']:
            if self.config.data['proxyUsername']:
                self.proxies = {
                    "https": "https://'" +
                             str(self.config.data['proxyUsername']) +
                             "':'" + str(self.config.data['proxyPassword']) +
                             "'@" + self.config.data['proxyURL'] + ':' +
                             str(self.config.data['proxyPort'])
                }
                self.proxiesMasked = {
                    "https": "https://'*******:*******@" +
                             self.config.data['proxyURL'] +
                             ':' + str(self.config.data['proxyPort'])
                }
                print(self.proxiesMasked)
            else:
                self.proxies = {
                    "https": 'https://' + self.config.data['proxyURL'] +
                             ':' + str(self.config.data['proxyPort'])
                }
                print(self.proxies)
        else:
            self.proxies = {}

    def get_session_token(self):
        """Return the session token"""
        return self.session_token

    def get_key_manager_token(self):
        """Return the key manager token"""
        return self.key_manager_token

    def authenticate(self):
        """Get the session and key manager token by calling APIs"""
        logging.debug('Auth/authenticate()')
        if self.last_auth_time == 0 or \
                int(round(time.time() * 1000) - self.last_auth_time >= 3000):
            logging.debug('Auth/authenticate() --> needed to authenticate')
            self.last_auth_time = int(round(time.time() * 1000))
            self.session_authenticate()
            self.key_manager_authenticate()
        else:
            try:
                logging.debug('Retry authentication in 30 seconds.')
                time.sleep(30)
                self.authenticate()
            except Exception as err:
                print(err)

    # Retrieve session token by calling the session token API
    # Certificates are passed in cert parameter
    def session_authenticate(self):
        """
        Get the session token by calling API, certificate data is
        passed in through Request Session object
        """
        logging.debug('Auth/get_session_token()')

        with Session() as session:
            session.mount(
                self.config.data['sessionAuthHost'],
                Pkcs12Adapter(
                    pkcs12_filename=self.config.data['p.12'],
                    pkcs12_password=self.config.data['botCertPassword']
                )
            )
            response = session.post(
                self.config.data['sessionAuthHost'] +
                '/sessionauth/v1/authenticate'
            )

        if response.status_code == 200:
            data = json.loads(response.text)
            logging.debug('Auth/session token success')
            self.session_token = data['token']
        else:
            logging.debug('Auth/get_session_token() failed: {}'.format(
                response.status_code)
            )
            self.session_authenticate()

    def key_manager_authenticate(self):
        """
        Get the key manager token by calling API, certificate data is
        passed in through Request Session object
        """
        logging.debug('Auth/get_keyauth()')

        with Session() as session:
            session.mount(
                self.config.data['sessionAuthHost'],
                Pkcs12Adapter(
                    pkcs12_filename=self.config.data['p.12'],
                    pkcs12_password=self.config.data['botCertPassword']
                )
            )
            response = session.post(
                self.config.data['sessionAuthHost'] +
                '/keyauth/v1/authenticate'
            )

        if response.status_code == 200:
            data = json.loads(response.text)
            logging.debug('Auth/keymanager token success')
            self.key_manager_token = data['token']
        else:
            logging.debug(
                'Auth/get_keyauth() failed: {}'.format(response.status_code)
            )
            self.key_manager_authenticate()
