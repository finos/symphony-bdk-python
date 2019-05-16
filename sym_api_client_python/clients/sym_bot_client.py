import requests
import json
import logging

from .datafeed_client import DataFeedClient
from ..datafeed_event_service import DataFeedEventService
from .message_client import MessageClient
from .stream_client import StreamClient
from .api_client import APIClient
from .user_client import UserClient
from ..exceptions.UnauthorizedException import UnauthorizedException

# SymBotClient class is the Client class that has access to all of the other
# client classes upon initialization, SymBotClient class gets an instance of
# each client along with access to all of its methods.
# class contains series of getters for each client
# class also contains config and auth class as a way to pass this info around
# to each client as well class is seen as orchestrator or interface for all
# REST API calls


class SymBotClient(APIClient):

    def __init__(self, auth, config):
        self.auth = auth
        self.config = config
        self.agentConfig = config
        self.datafeed_event_service = None
        self.datafeed_client = None
        self.msg_client = None
        self.stream_client = None
        self.user_client = None
        self.api_client = None
        self.pod_session = None
        self.agent_session = None
        self.bot_user_info = None

    def get_datafeed_event_service(self):
        if self.datafeed_event_service is None:
            self.datafeed_event_service = DataFeedEventService(self)
        return self.datafeed_event_service

    def get_datafeed_client(self):
        if self.datafeed_client is None:
            self.datafeed_client = DataFeedClient(self)
        return self.datafeed_client

    def get_message_client(self):
        if self.msg_client is None:
            self.msg_client = MessageClient(self)
        return self.msg_client

    def get_stream_client(self):
        if self.stream_client is None:
            self.stream_client = StreamClient(self)
        return self.stream_client

    def get_user_client(self):
        if self.user_client is None:
            self.user_client = UserClient(self)
        return self.user_client

    def get_api_client(self):
        self.api_client = APIClient(self)

    def get_sym_config(self):
        return self.config

    def get_sym_agent_config(self):
        return self.agentConfig

    def get_sym_auth(self):
        return self.auth

    def get_pod_session(self):
        if self.pod_session is None:
            self.pod_session = requests.Session()
            self.pod_session.headers.update({'sessionToken' : self.auth.get_session_token()})
            self.pod_session.proxies.update(self.config.data['podProxyRequestObject'])
            if (self.config.data['truststorePath']):
                logging.debug("Setting trusstorePath for pod to {}".format(self.config.data['truststorePath']))
                self.pod_session.verify=self.config.data['truststorePath']

        return self.pod_session

    def get_agent_session(self):
        if self.agent_session is None:
            self.agent_session = requests.Session()
            self.agent_session.headers.update(
                {'sessionToken' : self.auth.get_session_token(), 
                'keyManagerToken': self.auth.get_key_manager_token()
                })

            self.agent_session.proxies.update(self.config.data['agentProxyRequestObject'])
            if (self.config.data['truststorePath']):
                logging.debug("Setting trusstorePath for agent to {}".format(self.config.data['truststorePath']))
                self.agent_session.verify=self.config.data['truststorePath']

        return self.agent_session
    
    def execute_rest_call(self, method, path, **kwargs):
        results = None
        url = None
        session = None
        if path.startswith("/agent/"):
            url = self.config.data["agentHost"] + path
            session = self.get_agent_session()
        elif path.startswith("/pod/"):
            url = self.config.data["podHost"] + path
            session = self.get_pod_session()
        else:
            url = path
        
        response = session.request(method, url, **kwargs)
        if response.status_code == 204:
            results = []
        elif response.status_code == 200:
            results = json.loads(response.text)
        else:
            try:
                super().handle_error(response, self)
            except UnauthorizedException:
                self.execute_rest_call(method, path, **kwargs)
        return results

    def reauth_client(self):
        self.auth.authenticate()
        if (self.pod_session is not None):
            self.pod_session.headers.update({'sessionToken' : self.auth.get_session_token()})
        if (self.agent_session is not None):
            self.agent_session.headers.update(
                {'sessionToken' : self.auth.get_session_token(), 
                'keyManagerToken': self.auth.get_key_manager_token()
                })

    def get_bot_user_info(self):
        if (self.bot_user_info is None):
            self.bot_user_info = self.get_user_client().get_session_user()
        return self.bot_user_info
