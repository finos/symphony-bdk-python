import requests
import json
import logging
from .api_client import APIClient
from ..exceptions.UnauthorizedException import UnauthorizedException


# child class of APIClient --> Extends error handling functionality
class DataFeedClient(APIClient):

    def __init__(self, bot_client):
        self.bot_client = bot_client
        self.config = self.bot_client.get_sym_config()
        self.agent_proxies = self.config.data['agentProxyRequestObject']

    # raw api call to create_datafeed --> returns datafeed_id
    def create_datafeed(self):
        logging.debug('DataFeedClient/create_datafeed()')
        # messaging_logger.debug('DataFeedClient/create_datafeed()')
        headers = {
            'sessionToken': self.bot_client.get_sym_auth().get_session_token(),
            'keyManagerToken': self.bot_client.get_sym_auth().get_key_manager_token()
        }
        response = requests.post(
            self.config.data['agentHost'] + '/agent/v4/datafeed/create',
            proxies=self.agent_proxies, headers=headers
        )
        if response.status_code == 200:
            logging.debug(
                'DataFeedClient/create_datafeed() succeeded: {}'.format(response.status_code)
            )
            data = json.loads(response.text)
            datafeed_id = data['id']
            return datafeed_id

        else:
            try:
                logging.debug('DataFeedClient/create_datafeed() failed: {}'
                              .format(response.status_code))
                super().handle_error(response, self.bot_client)
            except UnauthorizedException:
                # should take 30 second to get here so after it
                # reauthorizes, catch it and re create df
                self.create_datafeed()

    # raw api call to read_datafeed --> returns an array of events returned
    # from DataFeed
    def read_datafeed(self, datafeed_id):
        logging.debug('DataFeedClient/read_datafeed()')
        datafeed_events = []
        headers = {
            'sessionToken':
                self.bot_client.get_sym_auth().get_session_token(),
            'keyManagerToken':
                self.bot_client.get_sym_auth().get_key_manager_token()
        }
        url = self.config.data['agentHost']+'/agent/v4/datafeed/{0}/read'.\
            format(datafeed_id)
        response = requests.get(url, headers=headers)
        if response.status_code == 204:
            datafeed_events = []
        elif response.status_code == 200:
            x = json.loads(response.text)
            datafeed_events.append(x)
        else:
            logging.debug(
                'DataFeedClient/read_datafeed() failed: {}'.
                    format(response.status_code)
            )
            super().handle_error(response, self.bot_client)

        return datafeed_events
