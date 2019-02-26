from .datafeed_client import DataFeedClient
from ..datafeed_event_service import DataFeedEventService
from .message_client import MessageClient
from .stream_client import StreamClient
from .api_client import APIClient
from .user_client import UserClient

# SymBotClient class is the Client class that has access to all of the other
# client classes upon initialization, SymBotClient class gets an instance of
# each client along with access to all of its methods.
# class contains series of getters for each client
# class also contains config and auth class as a way to pass this info around
# to each client as well class is seen as orchestrator or interface for all
# REST API calls


class SymBotClient:

    def __init__(self, auth, config):
        self.auth = auth
        self.config = config
        self.datafeed_event_service = None
        self.datafeed_client = None
        self.msg_client = None
        self.stream_client = None
        self.user_client = None
        self.api_client = None

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

    def get_sym_auth(self):
        return self.auth
