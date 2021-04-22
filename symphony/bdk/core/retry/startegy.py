from tenacity import retry_if_exception, retry_base, RetryCallState

from symphony.bdk.core.auth.exception import AuthUnauthorizedError
from symphony.bdk.gen import ApiException


class authentication_retry(retry_base):
    """Retry strategy that retries if the exception is not an ApiException error with a 401 status code.
    """

    def __init__(self):
        def is_unauthorized(exception):
            if isinstance(exception, AuthUnauthorizedError):
                cause = exception.cause
                return (
                        isinstance(cause, ApiException) and
                        cause.status == 401
                )

        self.predicate = is_unauthorized

    def __call__(self, retry_state: RetryCallState):
        if retry_state.outcome.failed:
            return not self.predicate(retry_state.outcome.exception())
        else:
            return False


def networkIssueMessageError(exception, address):
    pass
