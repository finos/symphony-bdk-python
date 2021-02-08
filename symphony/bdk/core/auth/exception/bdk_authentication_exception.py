"""Module containing all configuration related exception.
"""


class AuthInitializationException(Exception):
    """Thrown when unable to read/parse a RSA Private Key or a certificate.
    """

    def __init__(self, message: str):
        self.message = message


class AuthUnauthorizedException(Exception):
    """When thrown, it means that authentication cannot be performed for several reasons
    """

    def __init__(self, message: str, cause: Exception = None):
        self.message = message
        self.cause = cause
