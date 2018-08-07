import json
import requests
#library used to jwt signature
import logging
from jose import jwt
import datetime
import time
from ..clients.apiClient import APIClient
from ..exceptions.UnauthorizedException import UnauthorizedException

class SymBotRSAAuth(APIClient):
    #initialize with config object
    #get JWT token upon initization
    #fetch session and keymanager tokens respectively
    def __init__(self, config):
        self.config = config
        self.lastAuthTime=0
        if self.config.data['proxyURL']:
            self.proxies = {"http": self.config.data['proxyURL']}
            print(self.proxies)
        else:
            self.proxies = {}

    def getSessionToken(self):
        return self.sessionToken

    def getKeyManagerToken(self):
        return self.keyAuthToken


    def authenticate(self):
        logging.debug('Auth/authenticate()')
        if (self.lastAuthTime == 0) or (int(round(time.time() * 1000) - self.lastAuthTime>=3000)):
            logging.debug('Auth/authenticate() --> needed to authenticate')
            self.jwt = self.createJWT()
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

    #load .pem file generated on admin portal in symphony pod
    #retrieve folder of public/private keys by executing shell script on symphony developers guide
    #expiration_date is a timestamp LESS than 5 min in the future (IMPORTANT THAT ITS LESS)
    #function returns a signed JWT which can be used to authenticate bot
    def createJWT(self):
        logging.debug('RSA_auth/getJWT() function started')
        #load this from config
        with open(self.config.data['privatePemPath'], 'r') as f:
            privateKey = f.read()
            expiration_date = int(datetime.datetime.now(datetime.timezone.utc).timestamp() + (5*58))
            payload = {
                'sub': self.config.data['botUserName'],
                'exp': expiration_date
            }
            encoded = jwt.encode(payload, privateKey, algorithm='RS256')
            return encoded

    #raw api call to get session token.  pass jwt in request using json parameter
    def sessionAuthenticate(self):
        logging.debug('RSA_auth/get_session_token() function started')
        data = {
            'token': self.jwt
        }
        url = self.config.data['podHost']+'/login/pubkey/authenticate'
        print(url)
        response = requests.post(url, json=data, proxies=self.proxies)
        if response.status_code == 200:
            data = json.loads(response.text)
            logging.debug(data['token'])
            self.sessionToken = data['token']
        else:
            logging.debug('RSA_auth/get_session_token() function failed')
            self.authenticate()
    #raw api call to get key manager token.  pass jwt in request using json parameter
    def keyManagerAuthenticate(self):
        logging.debug('RSA_auth/get_keyauth() function started')
        data = {
            'token': self.jwt
        }
        url = self.config.data['keyAuthHost']+'/relay/pubkey/authenticate'
        print(url)
        response = requests.post(url, json=data, proxies=self.proxies)
        if response.status_code == 200:
            data = json.loads(response.text)
            logging.debug(data['token'])
            self.keyAuthToken = data['token']
        else:
            logging.debug('RSA_auth/get_keyauth() function failed')
            self.authenticate()
