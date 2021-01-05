import logging

from .api_client import APIClient


# child class of APIClient --> Extends error handling functionality
# SignalsClient class contains a series of functions corresponding to all
# pod admin endpoints on the REST API.
class SignalsClient(APIClient):

    def __init__(self, bot_client):
        self.bot_client = bot_client

    def list_signals(self, skip=0, limit=50):
        """
        Lists signals on behalf of the user. 
        The response includes signals that the user has created 
        and public signals to which they have subscribed.
        """
        logging.debug('SignalsClient/list_signals()')
        url = '/agent/v1/signals/list' 
        params = {'skip': skip, 'limit': limit}
        return self.bot_client.execute_rest_call("GET", url, params=params)

    def get_signal(self, signal_id):
        """
        Gets details about the specified signal.
        """
        logging.debug('SignalsClient/get_signal()')
        url = '/agent/v1/signals/{0}/get'.format(signal_id)
        return self.bot_client.execute_rest_call("GET", url)
    
    def create_signal(self, signal_object):
        """
        Creates a new Signal.

        Reference for the Signal Object:
        https://developers.symphony.com/restapi/reference#signal-object

        To create a company-wide signal, the requesting user needs to have the canCreatePushedSignals entitlement.

        To send numeric cashtags as signals, add a * before the number, for example, $*122450.
        """
        logging.debug('SignalClient/create_signal()')
        url = '/agent/v1/signals/create'
        return self.bot_client.execute_rest_call("POST", url, json=signal_object)
    
    def update_signal(self, signal_id, signal_object):
        """
        Updates an existing Signal.
        
        Reference for the Signal Object:
        https://developers.symphony.com/restapi/reference#signal-object

        To update a company-wide signal, the requesting user needs to have the canCreatePushedSignals entitlement.

        To update a normal signal, the requesting user needs to be the owner of the signal.

        To send numeric cashtags as signals, add a * before the number, for example, $*122450.
        """
        logging.debug('SignalsClient/update_signal()')
        url = '/agent/v1/signals/{0}/update'.format(signal_id)
        return self.bot_client.execute_rest_call("POST", url, json=signal_object)

    def delete_signal(self, signal_id):
        """Deletes an existing Signal."""
        logging.debug('SignalsClient/delete_signal()')
        url = '/agent/v1/signals/{0}/delete'.format(signal_id)
        return self.bot_client.execute_rest_call("POST", url)    

    def subscribe_signal(self, user_id_array, signal_id, pushed=False):
        """
        Subscribe an array of users to a Signal.
        
        To subscribe an entire pod to a Signal, set the companyWide field in Create Signal.

        To subscribe other users to a specific signal, 
        the requesting user needs to have the canManageSignalSubscription entitlement.
        """
        logging.debug('SignalsClient/subscribe_signal()')
        url = '/agent/v1/signals/{0}/subscribe'.format(signal_id)
        params = {"pushed": pushed}
        return self.bot_client.execute_rest_call("POST", url, params=params, json=user_id_array)

    
    def unsubscribe_signal(self, user_id_array, signal_id):
        """
        Unsubscribe an array of users from the specified Signal.
        
        To unsubscribe from a signal, the requesting user cannot be the owner of the signal.   

        To unsubscribe other users from a signal, the requesting user needs to have the canManageSignalSubscription entitlement and the signal cannot be a company-wide signal.
        """
        logging.debug('SignalsClient/unsubscribe_signal()')
        url = '/agent/v1/signals/{0}/unsubscribe'.format(signal_id)
        return self.bot_client.execute_rest_call("POST", url, json=user_id_array)


    def get_subscribers(self, signal_id, skip=0, limit=50):
        """ Gets the subscribers for the specified signal."""
        logging.debug('SignalsClient/get_subscribers()')
        url = '/agent/v1/signals/{0}/subscribers'.format(signal_id) 
        params = {'skip': skip, 'limit': limit}
        return self.bot_client.execute_rest_call("GET", url, params=params)
