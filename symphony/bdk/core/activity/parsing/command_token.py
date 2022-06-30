"""This module gathers all token classes that we can use for {@link SlashCommandPattern}
"""

import re
from abc import ABC, abstractmethod

from symphony.bdk.core.activity.parsing.message_entities import Cashtag, Hashtag, Mention

argument_name_pattern = re.compile(r"^[a-zA-Z_][a-zA-Z_$\d]*$")


class AbstractCommandToken(ABC):
    """
    Base class for all tokens that can be used in {@link SlashCommandPattern}.
    """

    @abstractmethod
    def matches(self, token: object):
        """
        Checks if the given input matches the token
        :param token: the input token, can be of type {@link String}, {@link Mention}, {@link Cashtag} or
                      {@link Hashtag}
        :return: Whether the input matches the token
        """


class ArgumentCommandToken(ABC):
    """
    Base class for all tokes that have an argument.
    """

    def __init__(self, arg_name: str):
        self._arg_name = arg_name

    @property
    def arg_name(self):
        return self._arg_name


class StaticCommandToken(AbstractCommandToken):
    """
    Command token only matching a given fixed word.
    """

    def __init__(self, pattern: str):
        if "{" in pattern or "}" in pattern:
            raise ValueError("Invalid pattern syntax")

        # Begin and end anchors added to the pattern
        self._pattern = "^" + pattern + "$"
        self._compiled_pattern = re.compile(r"" + self._pattern)

    def matches(self, token: object):
        return isinstance(token, str) and self._compiled_pattern.match(token)

    @property
    def pattern(self):
        return self._pattern

    def __eq__(self, o: object) -> bool:
        return isinstance(o, StaticCommandToken) and self._pattern == o._pattern


class StringArgumentCommandToken(AbstractCommandToken, ArgumentCommandToken):
    """
    A command token matching a single word and put in a given argument.
    """

    # at least one non-whitespace character
    whitespace_pattern = re.compile(r"^\S+$")

    def __init__(self, arg_name: str):
        # Remove the opening and closing brackets from the input to retrieve the name
        super().__init__(arg_name[1:-1])
        if not argument_name_pattern.match(self._arg_name):
            raise ValueError("Argument name is not valid")

    def matches(self, token: object):
        return isinstance(token, str) and StringArgumentCommandToken.whitespace_pattern.match(token)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, StringArgumentCommandToken) and self._arg_name == o._arg_name


class HashArgumentCommandToken(AbstractCommandToken, ArgumentCommandToken):
    """
    Command token only matching a Hashtag.
    """

    def __init__(self, arg_name: str):
        # Remove the opening and closing brackets and hash sign from the input to retrieve the name
        super().__init__(arg_name[2:-1])
        if not argument_name_pattern.match(self._arg_name):
            raise ValueError("Argument name is not valid")

    def matches(self, token: object):
        return isinstance(token, Hashtag)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, HashArgumentCommandToken) and self._arg_name == o._arg_name


class CashArgumentCommandToken(AbstractCommandToken, ArgumentCommandToken):
    """
    Command token only matching a Cashtag.
    """

    def __init__(self, arg_name: str):
        # Remove the opening and closing brackets and dollar sign from the input to retrieve the name
        super().__init__(arg_name[2:-1])
        if not argument_name_pattern.match(self._arg_name):
            raise ValueError("Argument name is not valid")

    def matches(self, token: object):
        return isinstance(token, Cashtag)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, CashArgumentCommandToken) and self._arg_name == o._arg_name


class MentionArgumentCommandToken(AbstractCommandToken, ArgumentCommandToken):
    """
    Command token only matching a Mention.
    """

    def __init__(self, arg_name: str):
        # Remove the opening and closing brackets and at sign from the input to retrieve the name
        super().__init__(arg_name[2:-1])
        if not argument_name_pattern.match(self._arg_name):
            raise ValueError("Argument name is not valid")

    def matches(self, token: object):
        return isinstance(token, Mention)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, MentionArgumentCommandToken) and self._arg_name == o._arg_name


class MatchingUserIdMentionToken(AbstractCommandToken):
    """
    Command token matching message token if it is a mention with a given user ID.
    """

    def __init__(self, bot_user_id_supplier):
        """
        :param bot_user_id_supplier: supplier function to get bot user id
        """
        self._matching_user_id_supplier = bot_user_id_supplier

    def matches(self, token: object):
        return isinstance(token, Mention) and token.user_id == self._matching_user_id_supplier()

    def __eq__(self, o: object) -> bool:
        return isinstance(o, MatchingUserIdMentionToken) and \
               self._matching_user_id_supplier() == o._matching_user_id_supplier()
