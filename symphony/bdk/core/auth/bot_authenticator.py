"""Module containing BotAuthenticator classes.
"""
from abc import ABC, abstractmethod

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.auth.exception import AuthUnauthorizedError
from symphony.bdk.core.auth.jwt_helper import create_signed_jwt
from symphony.bdk.core.config.model.bdk_bot_config import BdkBotConfig
from symphony.bdk.gen.api_client import ApiClient
from symphony.bdk.gen.auth_api.certificate_authentication_api import CertificateAuthenticationApi
from symphony.bdk.gen.exceptions import ApiException
from symphony.bdk.gen.login_api.authentication_api import AuthenticationApi
from symphony.bdk.gen.login_model.authenticate_request import AuthenticateRequest


class BotAuthenticator(ABC):
    """Bot authentication service.
    """

    def __init__(self, session_auth_client: ApiClient, key_manager_auth_client: ApiClient):
        self._session_auth_client = session_auth_client
        self._key_manager_auth_client = key_manager_auth_client

    async def authenticate_bot(self) -> AuthSession:
        """Authenticate a Bot's service account.

        :return: the authentication session.
        :rtype: AuthSession
        """
        auth_session = AuthSession(self)
        await auth_session.refresh()
        return auth_session

    async def retrieve_session_token(self) -> str:
        """Authenticates and retrieves a new session token.

        :return: the retrieved session token.
        """
        return await self._try_authenticate_and_get_token(self._session_auth_client)

    async def retrieve_key_manager_token(self) -> str:
        """Authenticated and retrieved a new key manager session.

        :return: the retrieved key manager session.
        """
        return await self._try_authenticate_and_get_token(self._key_manager_auth_client)

    async def _try_authenticate_and_get_token(self, api_client: ApiClient) -> str:
        try:
            return await self._authenticate_and_get_token(api_client)
        except ApiException as exc:
            unauthorized_message = "Service account is not authorized to authenticate. Check if credentials are valid."
            raise AuthUnauthorizedError(unauthorized_message, exc) from exc

    @abstractmethod
    async def _authenticate_and_get_token(self, api_client: ApiClient) -> str:
        """

        :param api_client: the api client instance to use to retrieve the token
          (either self._session_auth_client or self._key_manager_auth_client)
        :return: the token as a string
        """


class BotAuthenticatorRsa(BotAuthenticator):
    """Bot authenticator RSA implementation.
    """

    def __init__(self, bot_config: BdkBotConfig, login_api_client: ApiClient, relay_api_client: ApiClient):
        self._bot_config = bot_config
        super().__init__(login_api_client, relay_api_client)

    async def _authenticate_and_get_token(self, api_client: ApiClient) -> str:
        jwt = create_signed_jwt(self._bot_config.private_key, self._bot_config.username)
        req = AuthenticateRequest(token=jwt)

        token = await AuthenticationApi(api_client).pubkey_authenticate_post(req)
        return token.token


class BotAuthenticatorCert(BotAuthenticator):
    """Bot authenticator certificate implementation.
    """

    def __init__(self, session_auth_client: ApiClient, key_auth_client: ApiClient):
        super().__init__(session_auth_client, key_auth_client)

    async def _authenticate_and_get_token(self, api_client: ApiClient) -> str:
        token = await CertificateAuthenticationApi(api_client).v1_authenticate_post()
        return token.token
