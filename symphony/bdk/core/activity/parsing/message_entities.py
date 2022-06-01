"""This module gathers all entities that we can find in a message.
"""


class Cashtag:
    """
    Class representing a cashtag in a V4Message
    """

    def __init__(self, text, value):
        self._text = text
        self._value = value

    @property
    def text(self):
        return self._text

    @property
    def value(self):
        return self._value

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Cashtag) and self._text == o._text and self._value == o._value


class Hashtag:
    """
    Class representing a hashtag in a V4Message
    """

    def __init__(self, text, value):
        self._text = text
        self._value = value

    @property
    def text(self):
        return self._text

    @property
    def value(self):
        return self._value

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Hashtag) and self._text == o._text and self._value == o._value


class Mention:
    """
    Class representing a Mention in a V4Message
    """

    def __init__(self, text, user_id):
        self._text = text
        self._user_display_name = text[1:]
        self._user_id = user_id

    @property
    def text(self):
        return self._text

    @property
    def user_display_name(self):
        return self._user_display_name

    @property
    def user_id(self):
        return self._user_id

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Mention) \
               and self._text == o._text \
               and self._user_display_name == o._user_display_name \
               and self._user_id == o._user_id
