import logging
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
        try:
            x = response.json()
        except json.decoder.JSONDecodeError:
            logging.debug('JSON Decoding failed')
            x = response.text

        if response.status_code == 400 and 'Could not find a datafeed with the' in x['message']:
            logging.debug('datafeed expired, start_datafeed()')
            bot_client.datafeed_event_service.start_datafeed()

        elif response.status_code == 400:
            raise APIClientErrorException('Client Error Occurred: {}'
                                          .format(response.__dict__))

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
        elif response.status_code == 405:
            logging.debug('Handling 405 error')
            raise ForbiddenException(
                'Method Not Allowed: The method received in the request-line is known by the origin server but not supported by the target resource: {}'
                    .format(response.status_code))
        elif response.status_code >= 500:
            raise ServerErrorException(
                'Server Error Exception: {}'
                    .format(response.status_code))
        else:
            raise
