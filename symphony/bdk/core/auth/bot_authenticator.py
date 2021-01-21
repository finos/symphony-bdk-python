from abc import ABC, abstractmethod
from symphony.bdk.gen.login_api.authentication_api import AuthenticationApi
from symphony.bdk.gen.login_model.authenticate_request import AuthenticateRequest
from symphony.bdk.gen.exceptions import ApiException
from symphony.bdk.gen.api_client import ApiClient
from symphony.bdk.core.auth.jwt_helper import create_signed_jwt
from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.auth.exception.bdk_authentication_exception import AuthUnauthorizedException
from symphony.bdk.core.config.model.bdk_bot_config import BdkBotConfig


class BotAuthenticator(ABC):
    """Bot authentication service.
    """

    async def _retrieve_token(self, api_client: ApiClient) -> str:
        return await self._authenticate_and_get_token(api_client)

    @abstractmethod
    async def _authenticate_and_get_token(self, api_client: ApiClient) -> str:
        pass

    @abstractmethod
    async def authenticate_bot(self):
        pass


class BotAuthenticatorRSA(BotAuthenticator):
    """Bot authenticator RSA implementation.
    """

    def __init__(self, bot_config: BdkBotConfig, login_api_client: ApiClient, relay_api_client: ApiClient):
        self.bot_config = bot_config
        self.login_api_client = login_api_client
        self.relay_api_client = relay_api_client

    async def authenticate_bot(self) -> AuthSession:
        """Authenticate a Bot's service account.

        :return: the authentication session.
        """
        auth_session = AuthSession(self)
        await auth_session.refresh()
        return auth_session

    async def _authenticate_and_get_token(self, api_client: ApiClient) -> str:
        unauthorized_message = "Service account is not authorized to authenticate. Check if credentials are valid."
        jwt = create_signed_jwt(self.bot_config.private_key, self.bot_config.username)
        req = AuthenticateRequest(token=jwt)
        try:
            token = await AuthenticationApi(api_client).pubkey_authenticate_post(req)
            return token.token
        except ApiException:
            raise AuthUnauthorizedException(unauthorized_message)

    async def retrieve_session_token(self) -> str:
        """Make the api call to the pod to get the pod's session token.

        :return: The pod's session token
        """
        return await self._retrieve_token(self.login_api_client)

    async def retrieve_key_manager_token(self) -> str:
        """Make the api to the key manager server to get the key manager's token.

        :return: The key manager's token
        """
        return await self._retrieve_token(self.relay_api_client)
