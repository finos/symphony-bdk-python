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

    def handle_error(self, response, bot_client, error_json=None, text=None):

        _error_field = "message"
        if isinstance(response, requests.Response):
            status = response.status_code
        else:
            # The assumption is that it's an aiohttp response from an async request
            status = response.status
        
        try:
            if error_json is not None:
                try:
                    err_message = error_json[_error_field]
                except KeyError:
                    if text is not None:
                        err_message = text
                    else:
                        err_message = ""
            elif text is not None:
                err_message = text
            else:
                err_message = ""
                
        except Exception:
            logging.error("Unable to parse error message: {}".format(text))
            err_message = ""

        logging.debug('handle_error function started')
        if status == 400 and 'Could not find a datafeed with the' in err_message:
            logging.debug('datafeed expired, start_datafeed()')
            raise DatafeedExpiredException()

        # Response dict is a bit of an information overload, could consider trimming it
        elif status == 400:
            raise APIClientErrorException('Client Error Occurred: {}. Response contents: {}'
                                          .format(err_message, response.__dict__))
        # if HTTP = 401: reauthorize bot. Then raise UnauthorizedException
        elif status == 401:
            logging.debug('handling 401 error')
            bot_client.reauth_client()
            raise UnauthorizedException(
                'User, unauthorized, refreshing tokens: {}'
                    .format(status))
        elif status == 403:
            raise ForbiddenException(
                'Forbidden: Caller lacks necessary entitlement: {}'
                    .format(status))
        elif status == 405:
            logging.debug('Handling 405 error')
            raise ForbiddenException(
                'Method Not Allowed: The method received in the request-line is known by the origin server but not supported by the target resource: {}'
                    .format(status))
        elif status >= 500:
            raise ServerErrorException(
                'Server Error Exception: {}, {}'
                    .format(status, err_message))
        else:
            raise