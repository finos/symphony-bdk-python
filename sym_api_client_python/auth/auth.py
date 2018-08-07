import json
import requests
import logging
import time
from ..exceptions.UnauthorizedException import UnauthorizedException
# logging.basicConfig(filename='logs/example.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
# logging.getLogger("urllib3").setLevel(logging.WARNING)

class Auth():
    #initialize Auth object with config object and empty strings representing auth tokens
    def __init__(self, config):
        self.config = config
        self.lastAuthTime=0
        if self.config.data['proxyURL']:
            self.proxies = {"http": self.config.data['proxyURL']}
        else:
            self.proxies = {}

    def getSessionToken(self):
        return self.sessionToken

    def getKeyManagerToken(self):
        return self.keyAuthToken
    #if sessionToken or keyAuthToken are empty --> call auth endpoints below
    def authenticate(self):
        logging.debug('Auth/authenticate()')
        if (self.lastAuthTime == 0) or (int(round(time.time() * 1000) - self.lastAuthTime>=3000)):
            logging.debug('Auth/authenticate() --> needed to authenticate')
            self.lastAuthTime = int(round(time.time() * 1000))
            self.sessionAuthenticate()
            self.keyManagerAuthenticate()
        else:
            try:
                logging.debug('reauthenticated too fast. wait 30 seconds and try again.')
                time.sleep(30)
                self.authenticate()
            except Exception as err:
                print(err)




    #raw auth api call to retrieve session token
    #pass in certificates from config object using requests library built in cert parameter
    def sessionAuthenticate(self):
        logging.debug('Auth/get_session_token()')
        response = requests.post(self.config.data['sessionAuthHost']+'/sessionauth/v1/authenticate',proxies=self.proxies, cert=(self.config.data['symphonyCertificate'], self.config.data['symphonyKey']))
        if response.status_code == 200:
            data = json.loads(response.text)
            logging.debug('Auth/session token success: ' + data['token'])
            self.sessionToken = data['token']
        else:
            logging.debug('Auth/get_session_token() failed: {}'.format(response.status_code))
            self.authenticate()

    #raw auth api call to retrieve key manager token
    #pass in certificates from config object using requests library built in cert parameter
    def keyManagerAuthenticate(self):
        logging.debug('Auth/get_keyauth()')
        response = requests.post(self.config.data['keyAuthHost']+'/keyauth/v1/authenticate', proxies=self.proxies, cert=(self.config.data['symphonyCertificate'], self.config.data['symphonyKey']))
        if response.status_code == 200:
            data = json.loads(response.text)
            logging.debug('Auth/keymanager token sucess: ' + data['token'])
            self.keyAuthToken = data['token']
        else:
            logging.debug('Auth/get_keyauth() failed: {}'.format(response.status_code))
            self.authenticate()
