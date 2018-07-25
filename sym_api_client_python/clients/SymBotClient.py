from .DataFeedClient import DataFeedClient
from ..DataFeedEventService import DataFeedEventService
from .MessageClient import MessageClient
from .StreamClient import StreamClient
from .apiClient import APIClient
from .UserClient import UserClient

#SymBotClient class is the Client class that has access to all of the other client classes
#upon initialization, SymBotClient class gets an instance of each client along with access to all of its methods.
#class contains series of getters for each client
#class also contains config and auth class as a way to pass this info around to each client as well
#class is seen as orchestrator or interface for all REST API calls
class SymBotClient():

    def __init__(self, auth, config):
        self.auth = auth
        self.config = config
        self.dataFeedClient = None
        self.dataFeedEventService = None
        self.getAPIClient()
        self.getMessageClient()
        self.getStreamClient()
        self.getUserClient()


    def getDataFeedEventService(self):
        if self.dataFeedEventService is None:
            self.dataFeedEventService = DataFeedEventService(self)
        return self.dataFeedEventService

    def getDataFeedClient(self):
        if self.dataFeedClient is None:
            self.dataFeedClient = DataFeedClient(self)
        return self.dataFeedClient

    def getMessageClient(self):
        self.messageClient = MessageClient(self)

    def getStreamClient(self):
        self.streamClient = StreamClient(self)

    def getUserClient(self):
        self.userClient = UserClient(self)

    def getAPIClient(self):
        self.APIClient = APIClient(self)

    def getSymConfig(self):
        return self.config

    def getSymAuth(self):
        return self.auth
