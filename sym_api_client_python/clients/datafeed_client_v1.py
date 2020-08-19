import logging
from .api_client import APIClient


class DataFeedClientV1(APIClient):
    def __init__(self, bot_client):
        self.bot_client = bot_client

    # raw api call to create_datafeed --> returns datafeed_id
    def create_datafeed(self):

        url = '/agent/v4/datafeed/create'
        response = self.bot_client.execute_rest_call("POST", url)
        datafeed_id = response.get('id')
        logging.debug('DataFeedClientV1/create_datafeed() --> {}'.format(datafeed_id))
        return datafeed_id


    def read_datafeed(self, datafeed_id, *ackId):
        logging.debug('DataFeedClientV1/read_datafeed()')
        url = '/agent/v4/datafeed/{0}/read'.format(datafeed_id)
        datafeed_read = self.bot_client.execute_rest_call("GET", url)
        return datafeed_read

    def list_datafeed_id(self):
        logging.debug('DataFeedClientV1/list_datafeed_id()')
        raise TypeError("This function is not supported for the DF V1 client.")

    def delete_datafeed(self, datafeed_id):
        logging.debug('DataFeedClientV1/delete_datafeed()')
        raise TypeError("This function is not supported for the DF V1 client.")

    def get_ack_id(self):
        logging.debug('DataFeedClientV1/get_ack_id()')
        raise TypeError("This function is not supported for the DF V1 client.")


    async def read_datafeed_async(self, datafeed_id):

        logging.debug('DataFeedClientV1/read_datafeed_async()')
        url = '/agent/v4/datafeed/{0}/read'.format(datafeed_id)
        datafeed_read = await self.bot_client.execute_rest_call_async("GET", url)

        return datafeed_read

