import json
import logging


class SymConfig:
    # initialize object by passing in path to config file
    # store configuration data in variable data
    def __init__(self, path_to_config):
        self.path_to_config = path_to_config
        self.data = {}

    # load RSA configuration variables into SymConfig data
    def load_rsa_config(self):
        with open(self.path_to_config, "r") as read_file:
            data = json.load(read_file)
            self.data['sessionAuthHost'] = 'https://'+ data['sessionAuthHost'] + ':' + str(data['sessionAuthPort'])
            self.data['keyAuthHost'] = 'https://'+ data['keyAuthHost'] + ':' + str(data['keyAuthPort'])
            self.data['podHost'] = 'https://'+ data['podHost'] + ':' + str(data['podPort'])
            self.data['agentHost'] = 'https://'+ data['agentHost'] + ':' + str(data['agentPort'])
            self.data['botRSAPath'] = data['botRSAPath'] + data['botRSAName']
            self.data['botUsername'] = data['botUsername']
            self.data['botEmailAddress'] = data['botEmailAddress']
            self.data['proxyURL'] = data['proxyURL']
            self.data['proxyPort'] = data['proxyPort']
            self.data['proxyUsername'] = data['proxyUsername']
            self.data['proxyPassword'] = data['proxyPassword']
            self.data['truststorePath'] = data['truststorePath']
            self.data['completeProxyURL'] = self.build_proxy_url()
            
            read_file.close()

    # load Certificate configuration variables into SymConfig data
    def load_cert_config(self):
        with open(self.path_to_config, "r") as read_file:
            data = json.load(read_file)
            self.data['sessionAuthHost'] = 'https://'+ data['sessionAuthHost'] + ':' + str(data['sessionAuthPort'])
            self.data['keyAuthHost'] = 'https://'+ data['keyAuthHost'] + ':' + str(data['keyAuthPort'])
            self.data['podHost'] = 'https://'+ data['podHost'] + ':' + str(data['podPort'])
            self.data['agentHost'] = 'https://'+ data['agentHost'] + ':' + str(data['agentPort'])
            self.data['botCertPassword'] = data['botCertPassword']
            self.data['botEmailAddress'] = data['botEmailAddress']
            self.data['p.12'] = data['botCertPath'] + data['botCertName']
            self.data['proxyURL'] = data['proxyURL']
            self.data['proxyPort'] = data['proxyPort']
            self.data['proxyUsername'] = data['proxyUsername']
            self.data['proxyPassword'] = data['proxyPassword']
            self.data['truststorePath'] = data['truststorePath']
            self.data['completeProxyURL'] = self.build_proxy_url()

            read_file.close()

    def build_proxy_url(self):
        logging.debug('SymConfig/build_proxy_url()')
        proxy_builder = ""
        if (self.data['proxyURL']):
            proxy_builder = 'http://'
            if (self.data['proxyUsername']):
                proxy_builder += self.data['proxyUsername']
                if (self.data['proxyPassword']):
                    proxy_builder += ':' + self.data['proxyPassword']
                proxy_builder += '@' + self.data['proxyURL']
                if(self.data['proxyPort']):
                    proxy_builder += ':' + self.data['proxyPort']
        logging.debug('Proxy is set to: ' + proxy_builder)
        return proxy_builder