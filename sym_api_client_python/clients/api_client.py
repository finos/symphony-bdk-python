import logging
from ..exceptions.APIClientErrorException import APIClientErrorException
from ..exceptions.ServerErrorException import ServerErrorException
from ..exceptions.UnauthorizedException import UnauthorizedException
from ..exceptions.ForbiddenException import ForbiddenException
# error handling class --> take status code and raise appropriate exceptions
# this class acts as a parent class to each of the other client class.
# each child class extends error handling functionality


class APIClient:

    def __init__(self, bot_client):
        self.bot_client = bot_client

    def handle_error(self, response, bot_client):
        logging.debug('handle_error function started')
        if response.status_code == 400:
            raise APIClientErrorException('Client Error Occurred: {}'
                                          .format(response.__dict__))
        # if HTTP = 401: reauthorize bot. Then raise UnauthorizedException
        elif response.status_code == 401:
            logging.debug('handling 401 error')
            if not bot_client:
                bot_client.get_sym_auth().authenticate()
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
