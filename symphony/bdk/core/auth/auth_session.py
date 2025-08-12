"""Module containing session handle classes."""

import logging
from datetime import datetime, timezone

from symphony.bdk.core.auth.exception import AuthInitializationError
from symphony.bdk.core.auth.jwt_helper import extract_token_claims

logger = logging.getLogger(__name__)

EXPIRATION_SAFETY_BUFFER_SECONDS = 5
SKD_FLAG_NAME = "canUseSimplifiedKeyDelivery"


class AuthSession:
    """RSA Authentication session handle to get session and key manager tokens from.
    It uses a BotAuthenticator to actually retrieve the tokens when needed.
    """

    def __init__(self, authenticator):
        """

        :param authenticator: the :class:`symphony.bdk.core.auth.bot_authenticator.BotAuthenticator` instance to
          retrieve the tokens from.
        """
        self._session_token = None
        self._key_manager_token = None
        self._auth_token = None
        self._authenticator = authenticator
        self._expire_at = -1

    async def refresh(self):
        """Trigger re-authentication to refresh the tokens."""
        logger.debug("Authenticate")
        self._session_token = await self._authenticator.retrieve_session_token()
        if await self.skd_enabled:
            self._key_manager_token = ""
            return
        self.key_manager_token = await self._authenticator.retrieve_key_manager_token()

    @property
    async def session_token(self):
        """

        :return: the session token.
        """
        if self._session_token is None:
            self._session_token = await self._authenticator.retrieve_session_token()
        return self._session_token

    @property
    async def auth_token(self):
        """Auth token request calls the same endpoint that session token.
        Therefore, session token is updated unintentionally,
         since there's no explicit way to update authorization token exclusively
         : return: (str) authorization_token like Bearer eyJh...
        """

        if (
            self._auth_token
            and self._expire_at
            > datetime.now(timezone.utc).timestamp() + EXPIRATION_SAFETY_BUFFER_SECONDS
        ):
            return self._auth_token
        token, expire_at = await self._authenticator.retrieve_session_token_object()
        self._expire_at = expire_at
        self._auth_token = token.authorization_token
        self._session_token = token.token
        return self._auth_token

    @property
    async def key_manager_token(self):
        """

        :return: the key manager token
        """

        if await self.skd_enabled:
            return ""

        if self._key_manager_token is None:
            self._key_manager_token = await self._authenticator.retrieve_key_manager_token()
        return self._key_manager_token

    @session_token.setter
    def session_token(self, value):
        """Sets the session token. Used for testing purposes only.

        :param value: the new session token.
        """
        self._session_token = value

    @key_manager_token.setter
    def key_manager_token(self, value):
        """Sets the key manager token. Used for testing purposes only.

        :param value: the new key manager token.
        """
        self._key_manager_token = value

    @property
    async def skd_enabled(self):
        token_data = extract_token_claims(await self.session_token)
        if not token_data.get(SKD_FLAG_NAME, False):
            return False
        return await self._authenticator.agent_version_service.is_skd_supported()


class OboAuthSession(AuthSession):
    """RSA OBO Authentication session handle to get the OBO session token from.
    It uses an :class:`symphony.bdk.core.auth.obo_authenticator.OboAuthenticator` to actually retrieve the tokens when
    needed.
    """

    def __init__(self, authenticator, user_id: int = None, username: str = None):
        """At least user_id or username should be defined.

        :param authenticator: the :class:`symphony.bdk.core.auth.obo_authenticator.OboAuthenticator` instance to
          retrieve the tokens from.
        :param user_id: User Id.
        :param username: Username
        """
        super().__init__(authenticator)
        if user_id is not None and username is not None:
            raise AuthInitializationError(
                "Username and user id for OBO authentication should not be defined at a same time."
            )
        if user_id is None and username is None:
            raise AuthInitializationError(
                "At least username or user id should be defined for OBO authentication."
            )
        self.user_id = user_id
        self.username = username

    async def refresh(self):
        """Trigger re-authentication to refresh the OBO session token."""
        if self.user_id is not None:
            self._session_token = await self._authenticator.retrieve_obo_session_token_by_user_id(
                self.user_id
            )
        if self.username is not None:
            self._session_token = await self._authenticator.retrieve_obo_session_token_by_username(
                self.username
            )

    @property
    async def session_token(self):
        if self._session_token is None:
            await self.refresh()
        return self._session_token

    @property
    async def key_manager_token(self):
        """

        :return: an empty string since there is no key manager token in OBO mode.
        """
        return ""


class AppAuthSession:
    """Extension application RSA authentication handle to store the tokens. It uses a
    :class:`symphony.bdk.core.auth.ext_app_authenticator.ExtensionAppAuthenticator` to actually authenticate and
    retrieve the tokens.
    """

    def __init__(self, authenticator, app_token: str):
        """

        :param authenticator: the :class:`symphony.bdk.core.auth.ext_app_authenticator.ExtensionAppAuthenticator`
          which will actually perform the authentication
        :param app_token: the application token
        """
        self._authenticator = authenticator
        self._app_token = app_token
        self._expire_at = -1
        self._symphony_token = ""

    async def refresh(self) -> None:
        """Triggers re-authentication to refresh the tokens.

        :return: None
        """
        app_tokens = await self._authenticator.authenticate_and_retrieve_tokens(self._app_token)
        self._symphony_token = app_tokens.symphony_token
        self._app_token = app_tokens.app_token
        self._expire_at = app_tokens.expire_at

    @property
    def symphony_token(self) -> str:
        """

        :return: the Symphony token
        """
        return self._symphony_token

    @property
    def app_token(self) -> str:
        """

        :return: the application token
        """
        return self._app_token

    @property
    def expire_at(self) -> int:
        """

        :return: the Unix timestamp in milliseconds of the Symphony token expiration
        """
        return self._expire_at
