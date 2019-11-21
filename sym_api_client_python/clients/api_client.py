import logging
import asyncio
import requests
import json
from ..exceptions.APIClientErrorException import APIClientErrorException
from ..exceptions.ServerErrorException import ServerErrorException
from ..exceptions.UnauthorizedException import UnauthorizedException
from ..exceptions.ForbiddenException import ForbiddenException
from ..exceptions.DatafeedExpiredException import DatafeedExpiredException
from ..exceptions.MaxRetryException import MaxRetryException
# error handling class --> take status code and raise appropriate exceptions
# this class acts as a parent class to each of the other client class.
# each child class extends error handling functionality


class APIClient:

    def __init__(self, bot_client):
        self.bot_client = bot_client

    def handle_error(self, response, bot_client):
        logging.debug('handle_error function started')
        x = json.loads(response.text)
        
        if response.status_code == 400 and 'Could not find a datafeed with the' in x['message']:
            #no datafeed found, create new datafeedId and read from it
            bot_client.datafeed_event_service.start_datafeed()

        elif response.status_code == 400:
            raise APIClientErrorException('Client Error Occurred: {}'
                                          .format(response.__dict__))

        # if HTTP = 401: reauthorize bot. Then raise UnauthorizedException
        elif response.status_code == 401 and 'max auth retry limit:' in x['message']:
            logging.debug('handling 401 and max retry auth limit error')
            raise MaxRetryException('Max retry limit met')

        elif response.status_code == 401:
            logging.debug('handling 401 error')
            bot_client.reauth_client()
            raise UnauthorizedException(
                'User, unauthorized, refreshing tokens: {}'
                    .format(response.status_code))
        elif response.status_code == 403:
            raise ForbiddenException(
                'Forbidden: Caller lacks necessary entitlement: {}'
                    .format(response.status_code))
        elif response.status_code >= 500:
            raise ServerErrorException(
                'Server Error Exception: {}'
                    .format(response.status_code))
        else:
            raise
