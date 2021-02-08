class AuthSession:
    """RSA Authentication session handle to get session and key manager tokens from.
    It uses a BotAuthenticator to actually retrieve the tokens when needed.
    """

    def __init__(self, authenticator):
        """

        :param authenticator: the BotAuthenticator instance to retrieve the tokens from.
        """
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
        """

        :return: the session token.
        """
        if self._session_token is None:
            self._session_token = await self._authenticator.retrieve_session_token()
        return self._session_token

    @property
    async def key_manager_token(self):
        """

        :return: the key manager token
        """
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
