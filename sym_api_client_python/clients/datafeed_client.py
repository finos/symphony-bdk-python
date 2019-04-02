import requests
import json
import logging
from .api_client import APIClient
from ..exceptions.UnauthorizedException import UnauthorizedException


# child class of APIClient --> Extends error handling functionality
class DataFeedClient(APIClient):

    def __init__(self, bot_client):
        self.bot_client = bot_client

    # raw api call to create_datafeed --> returns datafeed_id
    def create_datafeed(self):
        logging.debug('DataFeedClient/create_datafeed()')
        # messaging_logger.debug('DataFeedClient/create_datafeed()')
        url = '/agent/v4/datafeed/create'
        response = self.bot_client.execute_rest_call("POST", url)
        return response['id']

    # raw api call to read_datafeed --> returns an array of events returned
    # from DataFeed
    def read_datafeed(self, datafeed_id):
        logging.debug('DataFeedClient/read_datafeed()')
        url = '/agent/v4/datafeed/{0}/read'.format(datafeed_id)
        new_events = []
        datafeed_read = self.bot_client.execute_rest_call("GET", url)
        if (datafeed_read != []):
            new_events.append(datafeed_read)
        return new_events