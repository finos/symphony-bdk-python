import logging

from .api_client import APIClient


# child class of APIClient --> Extends error handling functionality
# ConnectionsClient class contains a series of functions corresponding to all
# pod admin endpoints on the REST API.
class ConnectionsClient(APIClient):

    def __init__(self, bot_client):
        self.bot_client = bot_client

    def create_connection(self, user_id):
        """
        Pods from all users involved need to have crossPod enabled between them.

        Users who belong to the same private pod are implicitly connected.
        If you attempt to connect with an internal user, this endpoint will
        return the corresponding connection object with a status of accepted
        """
        logging.debug('ConnectionsClient/create_connection()')
        url = '/pod/v1/connection/create'
        data = {'userId': user_id}
        return self.bot_client.execute_rest_call('POST', url, json=data)

    def get_connection(self, user_id):
        """
        When calling this as an OBO-enabled endpoint,
        use the OBO User Authenticate token for sessionToken
        """
        logging.debug('ConnectionsClient/get_connection()')
        url = '/pod/v1/connection/user/{0}/info'.format(user_id)
        return self.bot_client.execute_rest_call('GET', url)

    def list_connections(self, status, **kwargs):
        """
        This retrieves all connections of the requesting user.
        (i.e. both connections in which the requesting user is the sender and
        those in which the requesting user is the inivtee).
        By default, if you haven't specified the connection status to filter on,
         this call will only return results for both "pending_incoming" and
         "pending_outgoing".
        """
        logging.debug('ConnectionsClient/list_connections()')
        url = '/pod/v1/connection/list'
        params = {'status' : status}
        return self.bot_client.execute_rest_call('GET', url, params=params)

    def accept_connection(self, user_id):
        """
        This allows the user to accept a specific connection request.
        For users of the same private pod who are implicitly connected,
        this endpoint returns the connection with status of "Accepted".
        """
        logging.debug('ConnectionsClient/accept_connection()')
        url = '/pod/v1/connection/accept'
        data = {'userId': user_id}
        return self.bot_client.execute_rest_call('POST', url, json=data)

    def reject_connection(self, user_id):
        """
        This allows the user to reject a specific connection request.
        Reject the connection between the requesting user and request sender.
        If both users are in the same private pod, an error will be returned
        because both users have an implicit connection which cannot be rejected.
        """
        logging.debug('ConnectionsClient/reject_connection()')
        url = '/pod/v1/connection/reject'
        data = {'userId': user_id}
        return self.bot_client.execute_rest_call('POST', url, json=data)

    def remove_connection(self, user_id):
        """
        Removes a connection with a user.
        This endpoint returns 400 Bad Request when the users aren't connected.
        For example, when a user hasn’t yet accepted a connection request
        from another user.
        """
        logging.debug('ConnectionsClient/remove_connection()')
        url = '/pod/v1/connection/user/{0}/remove'.format(user_id)
        return self.bot_client.execute_rest_call('POST', url)

