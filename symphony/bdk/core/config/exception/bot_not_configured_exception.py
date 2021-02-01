class BotNotConfiguredException(Exception):
    """Thrown when the bot configuration is not specified."""

    def __init__(self, message="Bot (service account) credentials have not been configured."):
        super().__init__(message)
