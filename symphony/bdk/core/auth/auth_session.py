class AuthSessionRSA:
    """
    RSA Authentication session handle.
    """

    def __init__(self, authenticator):
        self.__session_token = None
        self.__key_manager_token = None
        self.__authenticator = authenticator

    def get_session_token(self) -> str:
        """
        Get the pod's authentication token.

        Returns: the Pod session token.

        """
        return self.__session_token

    def get_key_manager_token(self) -> str:
        """
        Get the key manager's authentication token.

        Returns: the Key Manager token

        """
        return self.__key_manager_token

    async def refresh(self):
        """
        Trigger re-authentication to refresh the tokens.
        """
        self.__session_token = await self.__authenticator.retrieve_session_token()
        self.__key_manager_token = await self.__authenticator.retrieve_key_manager_token()
