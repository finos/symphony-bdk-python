import urllib

from tenacity import retry_if_exception

from symphony.bdk.core.auth.exception import AuthUnauthorizedError
from symphony.bdk.gen import ApiException


class authentication_retry_if_not_401(retry_if_exception):
    """Retry strategy that retries if the exception is an ApiException error with a 401 status code.
    """

    def __init__(self):
        def is_unauthorized(exception):
            if isinstance(exception, AuthUnauthorizedError):
                cause = exception.cause
                return (
                        isinstance(cause, ApiException) and
                        cause.status == 401
                )

        def should_retry(exception):
            unauthorized_message = "Service account is not authorized to authenticate. Check if credentials are valid."
            if is_unauthorized(exception):
                return False
            else:
                AuthUnauthorizedError(unauthorized_message, exc) from exc

        super().__init__(predicate=(not is_unauthorized))

    def networkIssueMessageError(self, exception, address):
        pass