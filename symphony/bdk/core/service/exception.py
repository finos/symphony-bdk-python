"""Module containing all service related exception.
"""


class MessageParserError(Exception):
    """Raised when the message is not found in the correct format
    """


class MessageCreationError(Exception):
    """Raised when a :py:class:`~symphony.bdk.core.service.message.model.Message` failed to be created
    """
