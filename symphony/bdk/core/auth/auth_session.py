class AuthSession:
    """RSA Authentication session handle.
    """

    def __init__(self, authenticator):
        self.session_token = None
        self.key_manager_token = None
        self._authenticator = authenticator

    async def refresh(self):
        """Trigger re-authentication to refresh the tokens.
        """
        self.session_token = await self._authenticator.retrieve_session_token()
        self.key_manager_token = await self._authenticator.retrieve_key_manager_token()
