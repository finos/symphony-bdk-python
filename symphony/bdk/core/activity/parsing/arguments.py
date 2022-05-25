from symphony.bdk.core.activity.parsing.message_entities import Mention, Hashtag, Cashtag


class Arguments:
    """
    Class storing arguments for {@link SlashCommandPattern}
    """

    def __init__(self, arguments=None):
        if arguments is None:
            arguments = {}
        self._arguments = arguments

    def get_argument_names(self):
        """
        Lists all argument names
        :return: List of argument names
        """
        return self._arguments.keys()

    def get(self, key: str):
        """
        Get an argument by key.
        :param key: Argument's name
        :return: Argument's value. It can be {@link String}, {@link Hashtag}, {@link Cashtag} or {@link Mention}.
                None if not found
        """
        return self._arguments.get(key)

    def get_as_string(self, key: str):
        """
        Get an argument as string.
        :param key: Argument's name
        :return: Argument's value as String. None if not found.
        """
        argument_value = self._arguments.get(key)
        if argument_value:
            return argument_value if isinstance(argument_value, str) else argument_value.text
        return None

    def get_string(self, key: str):
        """
        Get a string argument by key.
        :param key:  Argument's name
        :return: Argument's value. If it is not a String or not found, None is returned.
        """
        argument_value = self._arguments.get(key)
        if argument_value and isinstance(argument_value, str):
            return str(argument_value)
        return None

    def get_hashtag(self, key: str):
        """
        Get a hashtag argument by key.
        :param key: Argument's name
        :return: Argument's value. If it is not an instance of {@link Hashtag} or not found, None is returned.
        """
        argument_value = self._arguments.get(key)
        if argument_value and isinstance(argument_value, Hashtag):
            return argument_value
        return None

    def get_cashtag(self, key: str):
        """
        Get a cashtag argument by key.
        :param key: Argument's name
        :return: Argument's value. If it is not an instance of {@link Cashtag} or not found, None is returned.
        """
        argument_value = self._arguments.get(key)
        if argument_value and isinstance(argument_value, Cashtag):
            return argument_value
        return None

    def get_mention(self, key: str):
        """
        Get a mention argument by key.
        :param key: Argument's name
        :return: Argument's value. If it is not an instance of {@link Mention} or not found, None is returned.
        """
        argument_value = self._arguments.get(key)
        if argument_value and isinstance(argument_value, Mention):
            return argument_value
        return None

    def __eq__(self, other):
        return isinstance(other, Arguments) and self._arguments == other._arguments
