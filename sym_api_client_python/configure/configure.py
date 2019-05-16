import json


class SymConfig:
    # initialize object by passing in path to config file
    # store configuration data in variable data
    def __init__(self, path_to_config):
        self.path_to_config = path_to_config
        self.data = {}


    def load_config(self):
        with open(self.path_to_config, "r") as read_file:
            data = json.load(read_file)
            self.data = data

            if 'sessionAuthPort' in data:            
                self.data['sessionAuthHost'] = 'https://'+ data['sessionAuthHost'] + ':' + str(data['sessionAuthPort'])
            else: 
                self.data['sessionAuthHost'] = 'https://'+ data['sessionAuthHost']

            if 'keyAuthPort' in data:
                self.data['keyAuthHost'] = 'https://'+ data['keyAuthHost'] + ':' + str(data['keyAuthPort'])
            else:
                self.data['keyAuthHost'] = 'https://'+ data['keyAuthHost']
            
            if 'podPort' in data:
                self.data['podHost'] = 'https://'+ data['podHost'] + ':' + str(data['podPort'])
            else:
                self.data['podHost'] = 'https://'+ data['podHost']

            if 'agentPort' in data:        
                self.data['agentHost'] = 'https://'+ data['agentHost'] + ':' + str(data['agentPort'])
            else:
                self.data['agentHost'] = 'https://'+ data['agentHost']

            if 'botRSAName' in data:
                self.data['botRSAPath'] = data['botRSAPath'] + data['botRSAName']

            if 'botCertName' in data:
                self.data['p.12'] = data['botCertPath'] + data['botCertName']
            
            if 'proxyURL' in data:
                self.data['podProxyURL'] = data['proxyURL']
                self.data['podProxyUsername'] = data['proxyUsername'] if 'proxyUsername' in data else ""
                self.data['podProxyPassword'] = data['proxyPassword'] if 'proxyPassword' in data else ""
                self.data['agentProxyURL'] = data['proxyURL']
                self.data['agentProxyUsername'] = data['proxyUsername'] if 'proxyUsername' in data else ""
                self.data['agentProxyPassword'] = data['proxyPassword'] if 'proxyPassword' in data else ""
                self.data['keyManagerProxyURL'] = data['proxyURL']
                self.data['keyManagerProxyUsername'] = data['proxyUsername'] if 'proxyUsername' in data else ""
                self.data['keyManagerProxyPassword'] = data['proxyPassword'] if 'proxyPassword' in data else ""
        
    

            if 'podProxyURL' not in data or not data['podProxyURL']:
                self.data['podProxyRequestObject'] = {}
                self.data['podProxyURL'] = ""
            else:
                self.data['podProxyURL'] = data['podProxyURL']
                
                if 'podProxyUsername' in data and data['podProxyUsername']:
                    self.data['podProxyUsername'] = data['podProxyUsername']
                    self.data['podProxyPassword'] = data['podProxyPassword']
                    pod_proxy_parse = data['podProxyURL'].split('://')
                    pod_proxy_auth = data['podProxyUsername'] + ':' + data['podProxyPassword']
                    pod_proxy_url = pod_proxy_parse[0] + '://' + pod_proxy_auth + '@' + pod_proxy_parse[1]
                    self.data['podProxyRequestObject'] = {
                            'http' : pod_proxy_url,
                            'https' : pod_proxy_url,
                            }
                else:
                    self.data['podProxyRequestObject'] = {
                            'http' : data['podProxyURL'],
                            'https' : data['podProxyURL'],
                            }

            if 'agentProxyURL' not in data or not data['agentProxyURL']:
                self.data['agentProxyRequestObject'] = {}
                self.data['agentProxyURL'] = ""
            else:
                self.data['agentProxyURL'] = data['agentProxyURL']
                
                if 'agentProxyUsername' in data and data['agentProxyUsername']:
                    self.data['agentProxyUsername'] = data['agentProxyUsername']
                    self.data['agentProxyPassword'] = data['agentProxyPassword']
                    agent_proxy_parse = data['agentProxyURL'].split('://')
                    agent_proxy_auth = data['agentProxyUsername'] + ':' + data['agentProxyPassword']
                    agent_proxy_url = agent_proxy_parse[0] + '://' + agent_proxy_auth + '@' + agent_proxy_parse[1]
                    self.data['agentProxyRequestObject'] = {
                            'http' : agent_proxy_url,
                            'https' : agent_proxy_url,
                            }
                else:
                    self.data['agentProxyRequestObject'] = {
                            'http' : data['agentProxyURL'],
                            'https' : data['agentProxyURL'],
                            }

            if 'keyManagerProxyURL' not in data or not data['keyManagerProxyURL']:
                self.data['keyManagerProxyRequestObject'] = {}
                self.data['keyManagerProxyURL'] = ""
            else:
                self.data['keyManagerProxyURL'] = data['keyManagerProxyURL']
                
                if 'keyManagerProxyUsername' in data and data['keyManagerProxyUsername']:
                    self.data['keyManagerProxyUsername'] = data['keyManagerProxyUsername']
                    self.data['keyManagerProxyPassword'] = data['keyManagerProxyPassword']
                    km_proxy_parse = data['keyManagerProxyURL'].split('://')
                    km_proxy_auth = data['keyManagerProxyUsername'] + ':' + data['keyManagerProxyPassword']
                    km_proxy_url = km_proxy_parse[0] + '://' + km_proxy_auth + '@' + km_proxy_parse[1]
                    self.data['keyManagerProxyRequestObject'] = {
                            'http' : km_proxy_url,
                            'https' : km_proxy_url,
                            }
                else:
                    self.data['keyManagerProxyRequestObject'] = {
                            'http' : data['keyManagerProxyURL'],
                            'https' : data['keyManagerProxyURL'],
                            }
            print(json.dumps(self.data))

            read_file.close()

