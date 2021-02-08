class AuthSession:
    """RSA Authentication session handle.
    """

    def __init__(self, authenticator):
        self._session_token = None
        self._key_manager_token = None
        self._authenticator = authenticator

    async def refresh(self):
        """Trigger re-authentication to refresh the tokens.
        """
        self._session_token = await self._authenticator.retrieve_session_token()
        self._key_manager_token = await self._authenticator.retrieve_key_manager_token()

    @property
    async def session_token(self):
        if self._session_token is None:
            self._session_token = await self._authenticator.retrieve_session_token()
        return self._session_token

    @property
    async def key_manager_token(self):
        if self._key_manager_token is None:
            self._key_manager_token = await self._authenticator.retrieve_key_manager_token()
        return self._key_manager_token

    @session_token.setter
    def session_token(self, value):
        self._session_token = value

    @key_manager_token.setter
    def key_manager_token(self, value):
        self._key_manager_token = value


class OboAuthSession(AuthSession):
    """RSA OBO Authentication session handle.
    """

    def __init__(self, authenticator, user_id=None, username=None):
        super().__init__(authenticator)
        self.user_id = user_id
        self.username = username

    async def refresh(self):
        """Trigger re-authentication to refresh the OBO session token.
        """
        if self.user_id is not None:
            self._session_token = await self._authenticator.retrieve_obo_session_token_by_user_id(self.user_id)
        if self.username is not None:
            self._session_token = await self._authenticator.retrieve_obo_session_token_by_username(self.username)

    @property
    async def session_token(self):
        if self._session_token is None:
            if self.user_id is not None:
                self._session_token = await self._authenticator.retrieve_obo_session_token_by_user_id(self.user_id)
            if self.username is not None:
                self._session_token = await self._authenticator.retrieve_obo_session_token_by_username(self.username)
        return self._session_token

    @property
    async def key_manager_token(self):
        return self._key_manager_token

