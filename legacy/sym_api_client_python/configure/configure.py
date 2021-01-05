import json
import logging
import os

from sym_api_client_python.clients.constants.DatafeedVersion import DatafeedVersion


class SymConfig:
    # initialize object by passing in path to config file
    # store configuration data in variable data
    def __init__(self, path_to_config, relative_to=None):
        """If relative_to is supplied, all relative paths will be recomputed to be relative to the file or directory
        supplied. This allows starting the bots from other directories than where the main is. If a directory is
        given in this field, it should end with a slash.

        In testing one may want to set relative_to to be the path to the config json, so all references are relative
        to that. An application may wish to set this to __file__ in its main, meaning a configuration file from anywhere
        could be used.

        """
        self.path_to_config = path_to_config
        self.relative_to = os.path.dirname(relative_to) if relative_to is not None else os.curdir
        self.data = {}

    def _fix_relative_path(self, json_data, path_key, filename_key=None, warn_if_absent=True):
        """Given a json file, a key for a path and an optional key for a filename, extract the path
        and potentially name, resolve and join them. If warn_if_absent, issue a warning if the file
        or path does not exist at that location"""

        path = json_data[path_key]

        # Blank values are used to ignore entry. They should probably be None instead of blank but to maintain
        # backwards compatibility the function just returns "". If it continued "" would get resolved to "."
        if path == "":
            return ""

        if filename_key is not None:
            filename = json_data[filename_key]
            path = os.path.join(path, filename)
        result = os.path.normpath(os.path.join(self.relative_to, path))

        if warn_if_absent and (not os.path.exists(result)):
            parts = [p for p in [path_key, filename_key] if p is not None]
            logging.warning(
                "{} specified in config, but resolved path {} does not exist"
                    .format(", ".join(parts), result))
        return result

    def load_config(self):
        logging.debug("Loading config from: {}".format(os.path.realpath(self.path_to_config)))
        with open(self.path_to_config, "r") as read_file:
            data = json.load(read_file)
            self.data = data

            self.data['sessionAuthUrl'] = self._build_url(data.get('sessionAuthHost'), data.get('sessionAuthPort'),
                                                          data.get('sessionAuthContextPath'))
            self.data['keyAuthUrl'] = self._build_url(data.get('keyAuthHost'), data.get('keyAuthPort'),
                                                      data.get('keyAuthContextPath'))
            self.data['podUrl'] = self._build_url(data.get('podHost'), data.get('podPort'), data.get('podContextPath'))
            self.data['agentUrl'] = self._build_url(data.get('agentHost'), data.get('agentPort'),
                                                    data.get('agentContextPath'))

            # re-assign url to host to keep backward compatibility
            self.data['sessionAuthHost'] = self.data['sessionAuthUrl']
            self.data['keyAuthHost'] = self.data['keyAuthUrl']
            self.data['podHost'] = self.data['podUrl']
            self.data['agentHost'] = self.data['agentUrl']

            # backwards compatible
            if 'botCertPath' in data:
                self.data['botCertPath'] = self._fix_relative_path(data, 'botCertPath')

            if 'botRSAName' in data:
                self.data['botRSAPath'] = self._fix_relative_path(data, 'botRSAPath', 'botRSAName')

            if 'botPrivateKeyName' in data:
                self.data['botRSAPath'] = self._fix_relative_path(data, 'botPrivateKeyPath', 'botPrivateKeyName')

            if 'botCertName' in data:
                self.data['p.12'] = self._fix_relative_path(data, 'botCertPath', 'botCertName')

            if 'truststorePath' in data:
                self.data['truststorePath'] = self._fix_relative_path(data, 'truststorePath')

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
                        'http': pod_proxy_url,
                        'https': pod_proxy_url,
                    }
                else:
                    self.data['podProxyRequestObject'] = {
                        'http': data['podProxyURL'],
                        'https': data['podProxyURL'],
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
                        'http': agent_proxy_url,
                        'https': agent_proxy_url,
                    }
                else:
                    self.data['agentProxyRequestObject'] = {
                        'http': data['agentProxyURL'],
                        'https': data['agentProxyURL'],
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
                        'http': km_proxy_url,
                        'https': km_proxy_url,
                    }
                else:
                    self.data['keyManagerProxyRequestObject'] = {
                        'http': data['keyManagerProxyURL'],
                        'https': data['keyManagerProxyURL'],
                    }

            # datafeedVersion
            if "datafeedVersion" not in data:
                self.data["datafeedVersion"] = "v1"
            elif self.data.get("datafeedVersion").lower() == "v2":
                self.data["datafeedVersion"] = "v2"
            else:
                self.data["datafeedVersion"] = "v1"

            if 'datafeedEventsErrorTimeout' in data:
                self.data['datafeedEventsErrorTimeout'] = data['datafeedEventsErrorTimeout']

    def _build_url(self, host, port, contextPath):
        port = port if port else 443
        contextPath = contextPath if contextPath else ""

        if not (contextPath.startswith('/')):
            contextPath = '/' + contextPath
        if contextPath.endswith('/'):
            contextPath = contextPath[:-1]

        return 'https://' + host + ':' + str(port) + contextPath

    def get_agent_url(self):
        return self.data.get('agentUrl')

    def should_store_datafeed_id(self):
        return self.is_datafeed_v1() and self.is_datafeed_id_reused()

    def is_datafeed_v1(self):
        return DatafeedVersion.version_of(self.data.get("datafeedVersion")) != DatafeedVersion.V2

    def is_datafeed_id_reused(self):
        reuse_datafeed_id = self.data.get("reuseDatafeedID")
        return reuse_datafeed_id is None or reuse_datafeed_id

    def get_datafeed_id_folder_path(self):
        datafeed_id_file_path = self.data.get("datafeedIdFilePath")
        if datafeed_id_file_path:
            return datafeed_id_file_path
        return os.getcwd()
