import logging

from .api_client import APIClient
from .datafeed_client_v1 import DataFeedClientV1
from .datafeed_client_v2 import DataFeedClientV2


# child class of APIClient --> Extends error handling functionality
class DataFeedClient(APIClient):

    def __init__(self, bot_client):
        self.config = bot_client.get_sym_config()

        if self.config.is_datafeed_v1():
            self.datafeed_client = DataFeedClientV1(bot_client)
        else:
            self.datafeed_client = DataFeedClientV2(bot_client)

    # raw api call to create_datafeed --> returns datafeed_id
    def create_datafeed(self):
        """
        Create a new real time messages / events stream ("datafeed").
        The datafeed provides messages and events from all conversations that the user is in.
        The types of events surfaced in the datafeed can be found in the Real Time Events list.

        Returns the ID of the datafeed that has just been created. This ID should then be used as input to the Read Messages/Events Stream v4 endpoint.

        The datafeed will expire if it is not read before its capacity is reached.

        There is a maximum of 5 Datafeed per Service Account configured by default.
        This setting can be changed in the API Agent's property file.
        """
        return self.datafeed_client.create_datafeed()

    # raw api call to read_datafeed --> returns an array of events returned
    # from DataFeed
    def read_datafeed(self, datafeed_id, *ackId):
        """
        Reads messages from a given real time messages / events stream ("datafeed").

        The datafeed provides messages and events from all conversations that the user is in.
        The types of events surfaced in the datafeed can be found in the Real Time Events list.

        If no more messages are available, this method will be blocked for 30 seconds and return an HTTP 204 response (No Content) after. It is intended that the client should re-invoke this method as soon as it has processed the messages received in the previous call.
        If the client is able to consume messages more quickly than they become available, each call will be initially blocked and there is no need to delay before re-invoking this method.

        A datafeed will expire if its unread capacity is reached. For a standard datafeed, this will be 250 queued messages, and for firehose 500 messages.

        A datafeed can only be consumed by one client thread at a time. For example, polling the datafeed by two threads may lead to messages being delivered out of order.

        It is mandatory to read the datafeed from the same Agent instance that it was created on, bypassing any load balancer that may be in front of a multi-Agent configuration.

        The caller needs to be the same user that created the datafeed.

        There is no guarantee of message delivery for this endpoint. If errors occur while processing the request, either on the server or the API Agent, the messages that would have been returned may not be readable from the current stream. The messages are still available via the Messages endpoint and the Content Export function.

        """
        return self.datafeed_client.read_datafeed(datafeed_id, *ackId)

    def list_datafeed_id(self):
        """
        List datafeeds for a user's auth session.

        Returns
        -------
        Dictionary of datafeed ids a user is following. {"id": datafeed_id1, "id": datafeed_id2 ...}

        This feature is not supported in datafeed v1.
        """
        return self.datafeed_client.list_datafeed_id()

    def delete_datafeed(self, datafeed_id):
        """
        Delete a given datafeed

        Parameters
        ----------
        datafeed_id : int
            Datafeed id of the datafeed we want to delete.

        This feature is not supported in datafeed v1.
        """
        self.datafeed_client.delete_datafeed(datafeed_id)

    def get_ack_id(self):
        """
        Get the ack id for reading a V2 datafeed.

        This is stored in the DF client from the previous datafeed read.
        We give the user the freedom of altering the handling of the ack Id.

        Returns
        -------
        Ack id present in the previous read. Empty string if no read has been done

        This feature is not supported in datafeed v1.
        """
        return self.datafeed_client.get_ack_id()


    async def read_datafeed_async(self, datafeed_id):
        """
        This works the same as the previous datafeed apart from it's asynchronous and therefore should be called with the await keyword

        See read_datafeed for more info
        """
        return await self.datafeed_client.read_datafeed_async(datafeed_id)
