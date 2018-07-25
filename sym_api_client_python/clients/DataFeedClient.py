import requests
import json
from ..DataFeedEventService import DataFeedEventService
import logging
from .apiClient import APIClient
from ..exceptions.APIClientErrorException import APIClientErrorException
from ..exceptions.ForbiddenException import ForbiddenException
from ..exceptions.ServerErrorException import ServerErrorException
from ..exceptions.UnauthorizedException import UnauthorizedException


#child class of APIClient --> Extends error handling functionality
class DataFeedClient(APIClient):

    def __init__(self, botClient):
        self.botClient = botClient
        self.config = botClient.getSymConfig()
        self.auth = botClient.getSymAuth()

    #raw api call to createDatafeed --> returns dataFeedId
    def createDatafeed(self):
        logging.debug('DataFeedClient/createDatafeed()')
        # messaging_logger.debug('DataFeedClient/createDatafeed()')
        headers = {'sessionToken': self.auth.sessionToken, 'keyManagerToken': self.auth.keyAuthToken}
        response = requests.post(self.config.data['agentHost']+'/agent/v4/datafeed/create', headers=headers)

        if response.status_code == 200:
            data = json.loads(response.text)
            dataFeedId = data['id']
            return dataFeedId

        else:
            logging.debug('DataFeedClient/createDatafeed() failed: {}'.format(response.status_code))
            super().handleError(response)

    #raw api call to readDatafeed --> returns an array of events returned from DataFeed
    def readDatafeed(self, id):
        logging.debug('DataFeedClient/readDatafeed()')
        datafeedevents = []
        headers = {'sessionToken': self.auth.sessionToken, 'keyManagerToken': self.auth.keyAuthToken}
        url = self.config.data['agentHost']+'/agent/v4/datafeed/{0}/read'.format(id)
        response = requests.get(url, headers=headers )
        if (response.status_code == 204):
            datafeedevents = []
        elif(response.status_code == 200):
            x = json.loads(response.text)
            datafeedevents.append(x)

        else:
            logging.debug('DataFeedClient/readDatafeed() failed: {}'.format(response.status_code))
            super().handleError(response)

        return datafeedevents
