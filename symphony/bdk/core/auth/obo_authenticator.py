"""Module containing OBO authenticator classes."""

from abc import ABC, abstractmethod

from symphony.bdk.core.auth.auth_session import OboAuthSession
from symphony.bdk.core.auth.jwt_helper import create_signed_jwt
from symphony.bdk.core.config.model.bdk_app_config import BdkAppConfig
from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig
from symphony.bdk.core.retry import retry
from symphony.bdk.core.retry.strategy import authentication_retry
from symphony.bdk.gen.auth_api.certificate_authentication_api import (
    CertificateAuthenticationApi,
)
from symphony.bdk.gen.login_api.authentication_api import AuthenticationApi
from symphony.bdk.gen.login_model.authenticate_request import AuthenticateRequest


class OboAuthenticator(ABC):
    """Obo authentication service."""

    unauthorized_message = "Extension Application is not authorized to authenticate in OBO mode. Check if credentials are valid."

    @abstractmethod
    async def retrieve_obo_session_token_by_user_id(self, user_id: int) -> str:
        """Retrieve the OBO session token by username.

        :param user_id: User Id.
        :return: The obo session token.
        :raise AuthUnauthorizedError: if session token cannot be retrieved
        """

    @abstractmethod
    async def retrieve_obo_session_token_by_username(self, username: str) -> str:
        """Retrieve the OBO session token by username.

        :param username: Username
        :return: The obo session token.
        :raise AuthUnauthorizedError: if session token cannot be retrieved
        """

    def authenticate_by_username(self, username: str) -> OboAuthSession:
        """Authenticate On-Behalf-Of user by username.

        :param username: Username
        :return: the OBO authentication session.
        """
        return OboAuthSession(self, username=username)

    def authenticate_by_user_id(self, user_id: int) -> OboAuthSession:
        """Authenticate On-Behalf-Of user by user id.

        :param user_id: User Id
        :return: the OBO authentication session.
        """
        return OboAuthSession(self, user_id=user_id)


class OboAuthenticatorRsa(OboAuthenticator):
    """Obo authenticator RSA implementation."""

    def __init__(
        self,
        app_config: BdkAppConfig,
        authentication_api: AuthenticationApi,
        retry_config: BdkRetryConfig,
    ):
        self._app_config = app_config
        self._authentication_api = authentication_api
        self._retry_config = retry_config

    async def retrieve_obo_session_token_by_user_id(self, user_id: int) -> str:
        """Retrieve the OBO session token by user id.

        :param user_id: User Id.
        :return: The obo session token.
        :raise AuthUnauthorizedError: if session token cannot be retrieved
        """
        app_session_token = await self._authenticate_and_retrieve_app_session_token()
        return await self._authenticate_by_user_id(app_session_token, user_id=user_id)

    async def retrieve_obo_session_token_by_username(self, username: str) -> str:
        """Retrieve the OBO session token by username.

        :param username: Username
        :return: The obo session token.
        :raise AuthUnauthorizedError: if session token cannot be retrieved
        """
        app_session_token = await self._authenticate_and_retrieve_app_session_token()
        return await self._authenticate_by_username(
            app_session_token, username=username
        )

    @retry(retry=authentication_retry)
    async def _authenticate_and_retrieve_app_session_token(self) -> str:
        jwt = create_signed_jwt(self._app_config.private_key, self._app_config.app_id)
        req = AuthenticateRequest(token=jwt)

        token = await self._authentication_api.pubkey_app_authenticate_post(req)
        return token.token

    @retry(retry=authentication_retry)
    async def _authenticate_by_user_id(self, app_session_token, user_id) -> str:
        token = (
            await self._authentication_api.pubkey_app_user_user_id_authenticate_post(
                session_token=app_session_token, user_id=user_id
            )
        )
        return token.token

    @retry(retry=authentication_retry)
    async def _authenticate_by_username(self, app_session_token, username) -> str:
        token = await self._authentication_api.pubkey_app_username_username_authenticate_post(
            session_token=app_session_token, username=username
        )
        return token.token


class OboAuthenticatorCert(OboAuthenticator):
    """Obo authenticator Certificate implementation."""

    def __init__(
        self,
        certificate_authenticator_api: CertificateAuthenticationApi,
        retry_config: BdkRetryConfig,
    ):
        self._authentication_api = certificate_authenticator_api
        self._retry_config = retry_config

    @retry(retry=authentication_retry)
    async def retrieve_obo_session_token_by_user_id(self, user_id: int) -> str:
        """Retrieve the OBO session token by username.

        :param user_id: User Id.
        :return: The obo session token.
        :raise AuthUnauthorizedError: if session token cannot be retrieved
        """
        app_session_token = await self._retrieve_app_session_token()
        obo_auth = await self._authentication_api.v1_app_user_uid_authenticate_post(
            session_token=app_session_token, uid=user_id
        )
        return obo_auth.session_token

    @retry(retry=authentication_retry)
    async def retrieve_obo_session_token_by_username(self, username: str) -> str:
        """Retrieve the OBO session token by username.

        :param username: Username
        :return: The obo session token.
        :raise AuthUnauthorizedError: if session token cannot be retrieved
        """
        app_session_token = await self._retrieve_app_session_token()
        obo_auth = (
            await self._authentication_api.v1_app_username_username_authenticate_post(
                session_token=app_session_token, username=username
            )
        )
        return obo_auth.session_token

    @retry(retry=authentication_retry)
    async def _retrieve_app_session_token(self) -> str:
        token = await self._authentication_api.v1_app_authenticate_post()
        return token.token
