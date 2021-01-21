class AuthSession:
    """RSA Authentication session handle.
    """

    def __init__(self, authenticator):
        self._session_token = None
        self._key_manager_token = None
        self._authenticator = authenticator

    @property
    def session_token(self) -> str:
        """Get the pod's authentication token.

        :return: the Pod session token.
        """
        return self._session_token

    @property
    def key_manager_token(self) -> str:
        """Get the key manager's authentication token.

        :return: the Key Manager token
        """
        return self._key_manager_token

    async def refresh(self):
        """Trigger re-authentication to refresh the tokens.
        """
        self._session_token = await self._authenticator.retrieve_session_token()
        self._key_manager_token = await self._authenticator.retrieve_key_manager_token()
