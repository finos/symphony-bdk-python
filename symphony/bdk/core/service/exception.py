"""Module containing all service related exception.
"""


class MessageParserError(Exception):
    """Thrown when the message is not found in the correct format
    """

    def __init__(self, message: str):
        super().__init__()
        self.message = message
