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
