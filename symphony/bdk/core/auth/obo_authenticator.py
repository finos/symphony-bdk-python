from abc import ABC, abstractmethod

from symphony.bdk.core.auth.auth_session import OboAuthSession
from symphony.bdk.core.auth.exception import AuthUnauthorizedError
from symphony.bdk.core.auth.jwt_helper import create_signed_jwt
from symphony.bdk.core.config.model.bdk_app_config import BdkAppConfig
from symphony.bdk.gen.api_client import ApiClient
from symphony.bdk.gen.exceptions import ApiException
from symphony.bdk.gen.login_api.authentication_api import AuthenticationApi
from symphony.bdk.gen.login_model.authenticate_request import AuthenticateRequest


class OboAuthenticator(ABC):
    """Obo authentication service.
    """

    unauthorized_message = \
        "Extension Application is not authorized to authenticate in OBO mode. Check if credentials are valid."

    @abstractmethod
    async def _authenticate_and_retrieve_app_session_token(self):
        pass

    @abstractmethod
    async def _authenticate_and_retrieve_obo_session_token(
            self,
            app_session_token: str,
            username: str = None,
            user_id: int = None
    ):
        pass

    @abstractmethod
    async def retrieve_obo_session_token_by_user_id(
            self,
            user_id: int
    ):

        """
        Retrieve the OBO session token by username.

        :param user_id: User Id.

        :return: The obo session token.

        """

    @abstractmethod
    async def retrieve_obo_session_token_by_username(
            self,
            username: str
    ):
        """
        Retrieve the OBO session token by username.

        :param username: Username

        :return: The obo session token.

        """

    def authenticate_by_username(self, username: str):
        """Authenticate On-Behalf-Of user by username.

        :param username: Username

        :return: the OBO authentication session.
        """
        auth_session = OboAuthSession(self, username=username)
        return auth_session

    def authenticate_by_user_id(self, user_id: int):
        """Authenticate On-Behalf-Of user by user id.

        :param user_id: User Id

        :return: the OBO authentication session.
        """
        auth_session = OboAuthSession(self, user_id=user_id)
        return auth_session


class OboAuthenticatorRsa(OboAuthenticator):
    """Obo authenticator RSA implementation.
    """

    def __init__(self, app_config: BdkAppConfig, login_api_client: ApiClient):
        self._app_config = app_config
        self._authentication_api = AuthenticationApi(login_api_client)

    async def _authenticate_and_retrieve_app_session_token(self):
        jwt = create_signed_jwt(self._app_config.private_key, self._app_config.app_id)
        req = AuthenticateRequest(token=jwt)
        try:
            token = await self._authentication_api.pubkey_app_authenticate_post(req)
            return token.token
        except ApiException:
            raise AuthUnauthorizedError(self.unauthorized_message)

    async def _authenticate_and_retrieve_obo_session_token(
            self,
            app_session_token,
            username: str = None,
            user_id: int = None
    ):
        try:
            params = {
                'session_token': app_session_token
            }
            if user_id is not None:
                params['user_id'] = user_id
                token = await self._authentication_api.pubkey_app_user_user_id_authenticate_post(**params)
                return token.token
            if username is not None:
                params['username'] = username
                token = await self._authentication_api.pubkey_app_username_username_authenticate_post(**params)
                return token.token
        except ApiException:
            raise AuthUnauthorizedError(self.unauthorized_message)

    async def retrieve_obo_session_token_by_user_id(self, user_id: int):
        """
        Retrieve the OBO session token by user id.

        :param user_id: User Id.

        :return: The obo session token.

        """
        app_session_token = await self._authenticate_and_retrieve_app_session_token()
        return await self._authenticate_and_retrieve_obo_session_token(app_session_token, user_id=user_id)

    async def retrieve_obo_session_token_by_username(self, username: str):
        """
        Retrieve the OBO session token by username.

        :param username: Username

        :return: The obo session token.

        """
        app_session_token = await self._authenticate_and_retrieve_app_session_token()
        return await self._authenticate_and_retrieve_obo_session_token(app_session_token, username=username)
