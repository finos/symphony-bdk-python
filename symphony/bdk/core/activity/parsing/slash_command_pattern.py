import re

from symphony.bdk.core.activity.parsing.command_token import StaticCommandToken, StringArgumentCommandToken, \
    HashArgumentCommandToken, CashArgumentCommandToken, MentionArgumentCommandToken, ArgumentCommandToken
from symphony.bdk.core.activity.parsing.input_tokenizer import InputTokenizer
from symphony.bdk.core.activity.parsing.match_result import MatchResult
from symphony.bdk.gen.agent_model.v4_message import V4Message


class SlashCommandPattern:
    """
    Class representing the pattern of a {@link SlashCommandActivity}.
    The string should be a list of tokens separated by whitespaces. Each token can be:
    <ul>
        <li>a regular static word like "/command". This will only match the same string</li>
        <li>a string argument like "{argument}". This will match a single word (with no whitespaces)</li>
        <li>a mention argument like "{{@literal @}mention}. This will match a mention</li>
        <li>a cashtag argument like "{$cashtag}" which will match a cashtag</li>
        <li>a hashtag argument like "{#cashtag}" which will match a hashtag</li>
    </ul>
    """

    whitespace_pattern = re.compile(r"\s+")

    def __init__(self, pattern: str):
        self._tokens = [self.create_token(pattern) for pattern in
                        re.split(SlashCommandPattern.whitespace_pattern, pattern) if pattern]

        filtered_tokens_arg_names = list(filter(lambda a: a is not None, map(self.get_arg_name, self._tokens)))
        if not len(set(filtered_tokens_arg_names)) == len(filtered_tokens_arg_names):
            raise ValueError("Argument names must be unique")

    @staticmethod
    def get_arg_name(token):
        """

        :param token: the token passed in the pattern.
        :return: argument's name
        """
        if isinstance(token, ArgumentCommandToken):
            return token.arg_name
        return None

    @staticmethod
    def create_token(pattern):
        """

        :param pattern: pattern representing a token.
        :return: Token object corresponding to the given pattern.
        """
        if pattern.startswith("{") and pattern.endswith("}"):
            if pattern.startswith("{#"):
                return HashArgumentCommandToken(pattern)
            elif pattern.startswith("{$"):
                return CashArgumentCommandToken(pattern)
            elif pattern.startswith("{@"):
                return MentionArgumentCommandToken(pattern)
            else:
                return StringArgumentCommandToken(pattern)
        return StaticCommandToken(pattern)

    def get_match_result(self, message: V4Message):
        """

        :param message: The message to match the current pattern.
        :return: Whether the current pattern matches the given message.
        """
        input_tokenizer = InputTokenizer(message)
        input_tokens = input_tokenizer.tokens
        return MatchResult(True, self.get_arguments(input_tokens)) if self.matches(input_tokens) else MatchResult(False)

    def matches(self, input_tokens):
        """

        :param input_tokens: tokens from the input message.
        :return: Whether the whole tokens in the input are matching the tokens from the current pattern.
        """
        if len(input_tokens) != len(self._tokens):
            return False
        return self.matches_every_token(input_tokens)

    def matches_every_token(self, input_tokens):
        """

        :param input_tokens: tokens from the input message.
        :return: :return: Whether every token in the input matches the corresponding token from the current pattern.
        """
        for index in range(0, len(self.tokens)):
            if not self.tokens[index].matches(input_tokens[index]):
                return False
        return True

    def get_arguments(self, input_tokens):
        """

        :param input_tokens:
        :return: Map associating each argument name to the corresponding input token.
        """
        arguments = {}
        for index in range(0, len(self.tokens)):
            token = self.tokens[index]
            if isinstance(token, ArgumentCommandToken):
                arguments[token.arg_name] = input_tokens[index]
        return arguments

    def prepend_token(self, token):
        """

        :param token: token to be prepended.
        """
        self._tokens.insert(0, token)

    @property
    def tokens(self):
        return self._tokens
