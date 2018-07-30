import json
import requests
#library used to jwt signature
import logging
from jose import jwt
import datetime

class RSA_Auth():
    #initialize with config object
    #get JWT token upon initization
    #fetch session and keymanager tokens respectively
    def __init__(self, config):
        logging.basicConfig(filename='sym_api_client_python/logs/example.log', format='%(levelname)s: %(message)s', filemode='w', level=logging.DEBUG)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        self.config = config
        self.jwt = self.getJWT()
        self.sessionToken = self.get_session_token()
        self.keyAuthToken = self.get_keyauth()

    #load .pem file generated on admin portal in symphony pod
    #retrieve folder of public/private keys by executing shell script on symphony developers guide
    #expiration_date is a timestamp LESS than 5 min in the future (IMPORTANT THAT ITS LESS)
    #function returns a signed JWT which can be used to authenticate bot
    def getJWT(self):
        logging.debug('RSA_auth/getJWT() function started')
        #load this from config
        privateKey = open('reedBot/reedBot_privatekey.pem', 'r').read()
        expiration_date = int(datetime.datetime.now(datetime.timezone.utc).timestamp() + (5*58))
        payload = {
            'sub': 'reedBot',
            'exp': expiration_date
        }
        encoded = jwt.encode(payload, privateKey, algorithm='RS256')
        return encoded

    #raw api call to get session token.  pass jwt in request using json parameter
    def get_session_token(self):
        logging.debug('RSA_auth/get_session_token() function started')
        data = {
            'token': self.jwt
        }
        url = self.config.data['podHost']+'/login/pubkey/authenticate'
        response = requests.post(url, json=data)
        if response.status_code == 200:
            data = json.loads(response.text)
            return data['token']
        else:
            logging.debug('RSA_auth/get_session_token() function failed')
            raise Exception("Failed to get sessionToken: RSA")

    #raw api call to get key manager token.  pass jwt in request using json parameter
    def get_keyauth(self):
        logging.debug('RSA_auth/get_keyauth() function started')
        data = {
            'token': self.jwt
        }
        url = 'https://sup-km.symphony.com/relay/pubkey/authenticate'
        response = requests.post(url, json=data)
        if response.status_code == 200:
            data = json.loads(response.text)
            return data['token']
        else:
            logging.debug('RSA_auth/get_keyauth() function failed')
            raise Exception("Failed to get sessionToken: RSA")
