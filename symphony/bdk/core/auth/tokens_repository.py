"""Module which handles the storage of valid extension app tokens.
"""
from abc import ABC, abstractmethod


class TokensRepository(ABC):
    """Base abstract class to store and retrieve extension app tokens.
    """

    @abstractmethod
    async def save(self, app_token: str, symphony_token: str) -> None:
        """Saves a pair (app_token, symphony_token)

        :param app_token: the application token
        :param symphony_token: the Symphony token
        :return: None
        """

    @abstractmethod
    async def get(self, app_token: str) -> str:
        """Retrieves the corresponding Symphony token from a given application token.

        :param app_token: the application token
        :return: the symphony token corresponding to the app token if it exists, None otherwise
        """


class InMemoryTokensRepository(TokensRepository):
    """Class implementing an in-memory TokensRepository.
    """
    def __init__(self):
        self._tokens = {}

    async def save(self, app_token: str, symphony_token: str) -> None:
        self._tokens[app_token] = symphony_token

    async def get(self, app_token: str) -> str:
        return self._tokens.get(app_token)
