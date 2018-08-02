import json
import requests
#library used to jwt signature
import logging
from jose import jwt
import datetime
from ..clients.apiClient import APIClient
from ..exceptions.UnauthorizedException import UnauthorizedException

class SymBotRSAAuth(APIClient):
    #initialize with config object
    #get JWT token upon initization
    #fetch session and keymanager tokens respectively
    def __init__(self, config):
        self.config = config
        self.sessionToken = ''
        self.keyAuthToken = ''
        self.jwt = self.getJWT()
        if self.config.data['proxyURL']:
            self.proxies = {"http": self.config.data['proxyURL']}
            print(self.proxies)
        else:
            self.proxies = {}


    def authenticate(self):
        if not(self.sessionToken or self.keyAuthToken):
            logging.debug('Auth/authenticate() --> needed to authenticate')
            self.sessionToken = self.get_session_token()
            self.keyAuthToken = self.get_keyauth()
        else:
            logging.debug('Auth/authenticate() --> did not need to authenticate')

    #load .pem file generated on admin portal in symphony pod
    #retrieve folder of public/private keys by executing shell script on symphony developers guide
    #expiration_date is a timestamp LESS than 5 min in the future (IMPORTANT THAT ITS LESS)
    #function returns a signed JWT which can be used to authenticate bot
    def getJWT(self):
        logging.debug('RSA_auth/getJWT() function started')
        #load this from config
        privateKey = open(self.config.data['privatePemPath'], 'r').read()
        print(privateKey)
        expiration_date = int(datetime.datetime.now(datetime.timezone.utc).timestamp() + (5*58))
        payload = {
            'sub': self.config.data['botUserName'],
            'exp': expiration_date
        }
        encoded = jwt.encode(payload, privateKey, algorithm='RS256')
        return encoded

    #raw api call to get session token.  pass jwt in request using json parameter
    def get_session_token(self):
        logging.debug('RSA_auth/get_session_token() function started')
        print(self.jwt)
        data = {
            'token': self.jwt
        }
        url = self.config.data['podHost']+'/login/pubkey/authenticate'
        print(url)
        response = requests.post(url, json=data, proxies=self.proxies)
        if response.status_code == 200:
            data = json.loads(response.text)
            return data['token']
        else:
            logging.debug('RSA_auth/get_session_token() function failed')
            raise Exception("Failed to get sessionToken: RSA: {}".format(response.status_code))

    #raw api call to get key manager token.  pass jwt in request using json parameter
    def get_keyauth(self):
        logging.debug('RSA_auth/get_keyauth() function started')
        data = {
            'token': self.jwt
        }
        url = self.config.data['podHost']+'/relay/pubkey/authenticate'
        print(url)
        response = requests.post(url, json=data, proxies=self.proxies)
        if response.status_code == 200:
            data = json.loads(response.text)
            return data['token']
        else:
            logging.debug('RSA_auth/get_keyauth() function failed')
            raise Exception("Failed to get sessionToken: RSA")
