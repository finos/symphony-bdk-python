"""Module containing all configuration related exception.
"""


class BdkConfigError(Exception):
    """Exception class raised when configuration is invalid.
    """


class BotNotConfiguredError(Exception):
    """Thrown when the bot configuration is not specified."""

    def __init__(self, message="Bot (service account) credentials have not been configured."):
        super().__init__()
        self.message = message
