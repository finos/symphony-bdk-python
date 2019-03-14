import json


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
            read_file.close()
