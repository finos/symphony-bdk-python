from symphony.bdk.core.activity.parsing.arguments import Arguments


class MatchResult:
    """
    Class representing the outcome of a matching between a {@link SlashCommandPattern} and a message.
    It can contain the map of arguments if applicable. Key is argument name, value is the actual value in the message.
    Argument value can be of type {@link String}, {@link Mention}, {@link Cashtag} or {@link Hashtag}.
    """

    def __init__(self, is_matching: bool, arguments=None):
        self._is_matching = is_matching
        if is_matching and arguments:
            self._arguments = Arguments(arguments)
        else:
            self._arguments = None

    @property
    def is_matching(self):
        return self._is_matching

    @property
    def arguments(self):
        return self._arguments

    def __eq__(self, other):
        return isinstance(other, MatchResult) \
               and self._is_matching == other._is_matching \
               and self._arguments == other._arguments
