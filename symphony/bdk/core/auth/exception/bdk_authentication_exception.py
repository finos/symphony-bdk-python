class AuthInitializationException(Exception):
    """
    Thrown when unable to read/parse a RSA Private Key or a certificate.
    """
    pass


class AuthUnauthorizedException(Exception):
    """
    When thrown, it means that authentication cannot be performed for several reasons
    """
    pass
