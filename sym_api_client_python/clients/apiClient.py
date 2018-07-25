# from clients import SymBotClient
import logging
from ..exceptions.APIClientErrorException import APIClientErrorException
from ..exceptions.ServerErrorException import ServerErrorException
from ..exceptions.UnauthorizedException import UnauthorizedException
from ..exceptions.ForbiddenException import ForbiddenException
# logging.basicConfig(filename='..logs/example.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
# logging.getLogger("urllib3").setLevel(logging.WARNING)
#error handling class --> take status code and raise appropriate exceptions
#this class acts as a parent class to each of the other client class.
#each child class extends error handling functionality
class APIClient():

    def __init__(self, botClient):
        self.botClient = botClient

    def handleError(self, response):
        logging.debug('handleError function started')
        if response.status_code == 400:
            raise APIClientErrorException('Client Error Occured: {}'.format(response.status_code))
        #if HTTP = 401: reauthorize bot. Then raise UnauthorizedException
        elif response.status_code == 401:
            self.botClient.getSymAuth().authenticate()
            raise UnauthorizedException('User, unauthorized, refreshing tokens: {}'.format(response.status_code))
        elif response.status_code == 403:
            raise ForbiddenException('Forbidden: Caller lacks necessary entitlement: {}'.format(response.status_code))
        elif response.status_code == 500:
            raise ServerErrorException('Server Error Exception: {}'.format(response.status_code))

        else:
            logging.debug('unknown error: {}'.format(response.status_code))
