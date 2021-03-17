"""Module containing all authentication related exception.
"""


class AuthInitializationError(Exception):
    """Thrown when unable to read/parse a RSA Private Key or a certificate.
    """

    def __init__(self, message: str):
        super().__init__()
        self.message = message


class AuthUnauthorizedError(Exception):
    """When thrown, it means that authentication cannot be performed for several reasons
    """

    def __init__(self, message: str, cause: Exception = None):
        super().__init__()
        self.message = message
        self.cause = cause
