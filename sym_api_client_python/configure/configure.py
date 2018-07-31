import json
import requests
import sys
import logging
# from configure.crypt import Crypt
from ..configure.crypt import Crypt

class Config():
    #initialize object by passing in config file
    #store info in config file in dict called data
    def __init__(self, configFile):
        self.configFile = configFile
        self.data = {}

    #print dictionary --> convenience function for debugging purposes
    def printdata(self):
        for k,v in self.data.items():
            print(v)

    #read config file and store values in dictionary called data
    #sessionAuthUrl, keyAuthUrl, are endpoints used for authentication respectively
    #podHost and agentHost are used for any of the other REST API requests
    def connect(self):
        with open(self.configFile, "r") as read_file:
            data = json.load(read_file)
            self.data['sessionAuthUrl'] = 'https://'+ data['sessionAuthHost']
            self.data['keyAuthUrl'] = 'https://'+ data['keyAuthHost']
            self.data['podHost'] = 'https://'+ data['podHost']
            self.data['agentHost'] = 'https://'+ data['agentHost']
            self.data['botCertPath'] = data['botCertPath'] + data['botCertName']
            self.data['botCertName'] = data['botCertName']
            self.data['botCertPassword'] = data['botCertPassword']
            self.data['botEmailAddress'] = data['botEmailAddress']
            self.data['p.12'] = self.data['botCertPath'] + '.p12'
        #take in .p12 certificate and parse through file to use for authentication
        #data['botCert_cert'] and data['botCert_key'] are passed as certificates upon authentication request
        try:
            logging.debug('p.12 --->  ' + self.data['p.12'])
            crypt = Crypt(self.data['p.12'], self.data['botCertPassword'])
            self.data['symphonyCertificate'], self.data['symphonyKey'] = crypt.p12parse()


        except Exception as err:
            print("Failed to load config file: %s" % err)
            raise
