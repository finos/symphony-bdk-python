from .api_client import APIClient
import logging
import json

class DataFeedClientV2(APIClient):
    def __init__(self, bot_client):
        self.bot_client = bot_client
        self.ackid = ""

    def create_datafeed(self):
        url = '/agent/v5/datafeeds'
        response = self.bot_client.execute_rest_call("POST", url)

        datafeed_id = response.get("id")
        logging.debug('DataFeedClientV2/create_datafeed() --> {}'.format(datafeed_id))
        return datafeed_id


    def read_datafeed(self, datafeed_id, *ackId):
        """
        DF 2 Version: We need to use an ack Id to make sure the events are well received
        """
        logging.debug('DataFeedClientV2/read_datafeed()')
        url = '/agent/v5/datafeeds/{0}/read'.format(datafeed_id)
        data = {}
        if len(ackId) == 0:
            data["ackId"] = ""
        else:
            data["ackId"] = ackId[0]

        datafeed_read = self.bot_client.execute_rest_call("POST", url,  json=data)
        self.ackid = datafeed_read.get("ackId")
        events = datafeed_read.get("events")
        return events

    def list_datafeed_id(self):
        logging.debug('DataFeedClientV2/list_datafeed()')
        url = '/agent/v5/datafeeds'
        datafeed_ids = self.bot_client.execute_rest_call("GET", url)
        return datafeed_ids

    def delete_datafeed(self, datafeed_id):
        logging.debug('DataFeedClientV2/delete_datafeed()')
        url = '/agent/v5/datafeeds/{0}'.format(datafeed_id)
        self.bot_client.execute_rest_call("DELETE", url)

    def get_ack_id(self):
        return self.ackid