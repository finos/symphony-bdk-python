import logging

from .api_client import APIClient


# child class of APIClient --> Extends error handling functionality
# PresenceClient class contains a series of functions corresponding to all
# pod admin endpoints on the REST API.
class PresenceClient(APIClient):

    def __init__(self, bot_client):
        self.bot_client = bot_client

    def get_presence(self):
        """Returns the online status of the calling user."""
        logging.debug('PresenceClient/get_presence()')
        url = '/pod/v2/user/presence/'

        return self.bot_client.execute_rest_call('GET', url)

    def get_all_presence(self, last_user_id, limit):
        """
        Returns the presence of all users in a pod

        lastUserId - Last user ID retrieved, used for paging. If provided, results skip users with IDs less than this parameter.

        limit - Maximum number of records to return. The maximum supported value is 5000.

        All non-inactive users are returned and some inactive users may be included. Any omitted user is inactive.

        Only users with the User Provisioning role can call this endpoint
        """
        logging.debug('PresenceClient/get_all_presence()')
        url = '/pod/v2/users/presence'
        params = {
                'lastUserId': last_user_id,
                'limit': limit
                }
        return self.bot_client.execute_rest_call('GET', url, params=params)

    def get_user_status(self, user_id, local=True):
        """
        Returns the online status of the specified user.


        local
        true: Perform a local query and set the presence to OFFLINE for users who are not local to the calling user’s pod.
        false or absent: Query the presence of all local and external users who are connected to the calling user. See also Query Presence of External Users.
        
        The timestamp in the response is in UTC format and contains the time when the presence was set using Set Presence. For users who are offline, the timestamp contains the current time when the Get User Presence endpoint was invoked.

        To get the presence of external users, you must first register interest about their presence.

        When calling this as an OBO-enabled endpoint, use the OBO User Authenticate token for sessionToken.

    The available online status values (presence categories) for users are listed on the Get Presence page.

        Query Presence of External Users
    To query the presence of external users, you must first perform an additional step:
        1. Call the Register Interest in External User Presence endpoint to register interest in those users.
        2. Call this endpoint to query the presence of each user.

        To query the presence of internal users, you do not need to register interest and can call this endpoint directly.
        """
        logging.debug('PresenceClient/get_user_status()')
        url = '/pod/v3/user/{0}/presence'.format(user_id)
        params = {'local': local}
        return self.bot_client.execute_rest_call("GET", url, params=params)

    def external_presence_interest(self, array_user_ids):
        """
        To get the presence state of external users, you must first register interest in those users using this endpoint.

        Any user can see the presence of other users of the same company. For users of a different company, the two users must be connected to see presence.

        To query the presence of external users:
        1. Call this endpoint to register interest in the desired users.
        2. Call the Get User Presence endpoint to query the presence of each user.
        To keep the registration active, call this endpoint every hour.

        To query the presence of internal users, you do not need to register interest.
        Rate Limit
Getting an external user’s presence is limited to one call every 5 minutes.

        Roles and Privileges
        Calling this endpoint requires the ADMIN_PRESENCE_UPDATE privilege.
        See Permissions for a list of roles and associated privileges.
        """
        logging.debug('PresenceClient/external_presence_interest()')
        url = '/pod/v1/user/presence/register'
        data = {'userIds': array_user_ids}
        return self.bot_client.execute_rest_call("POST", url, json=data)

    def set_presence(self, category):
        """
        Sets the online status of the calling user.

        category*
        The new presence state for the user. Possible values are AVAILABLE, BUSY, AWAY, ON_THE_PHONE, BE_RIGHT_BACK, IN_A_MEETING, OUT_OF_OFFICE, OFF_WORK.
        
        Calling this endpoint requires the ADMIN_PRESENCE_UPDATE privilege.
        See Permissions for a list of roles and associated privileges.
        """
        logging.debug('PresenceClient/set_presence()')
        url = '/pod/v2/user/presence'
        data = {'category': category}
        return self.bot_client.execute_rest_call("POST", url, json=data)

    def create_presence_feed(self):
        """
        Creates a new stream capturing online status changes ("presence feed") for the company (pod) and returns the ID of the new feed. 
        The feed will return the presence of users whose presence status has changed since it was last read.
        """
        logging.debug('PresenceClient/create_presence_feed()')
        url = '/pod/v1/presence/feed/create'
        return self.bot_client.execute_rest_call("POST", url)

    def read_presence_feed(self, feed_id):
        """
        Reads the specified presence feed that was created using the Create Presence feed endpoint. 
        The feed returned includes the user presence statuses that have changed since they were last read.
        """
        logging.debug('PresenceClient/read_presence_feed()')
        url = '/pod/v1/presence/feed/{0}/read'.format(feed_id)
        return self.bot_client.execute_rest_call("GET", url)


    def delete_presence_feed(self, feed_id):
        """
        Deletes a presence status feed. 
        This endpoint returns the ID of the deleted feed if the deletion is successful.
        """
        logging.debug('PresenceClient/delete_presence_feed()')
        url = '/pod/v1/presence/feed/{0}/delete'.format(feed_id)
        return self.bot_client.execute_rest_call("GET", url)

    def set_user_presence(self, user_id, category):
        """
        Sets the presence state of a another user.

        To set the presence of another user, this endpoint requires to be called by a service user with the "User Provisioning" Entitlement.
        """
        logging.debug('PresenceClient/set_user_presence()')
        url = '/pod/v3/user/presence'
        data = {
                'category': category,
                'userId': user_id
                }
        return self.bot_client.execute_rest_call("POST", url, json=data)
