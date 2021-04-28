from aiohttp import ClientConnectorError
from tenacity import RetryCallState

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.auth.exception import AuthUnauthorizedError
from symphony.bdk.gen import ApiException


def is_unauthorized(exception: ApiException) -> bool:
    return exception.status == 401


def is_client_error(exception: ApiException) -> bool:
    return exception.status == 400


def is_network_or_minor_error(exception: Exception) -> bool:
    """Checks if the exception is a network issue or an :py:class:`ApiException` minor error
    This is the default function used to check if a given exception should lead to a retry

    :param exception: The exception to be checked
    :return:
    """
    if isinstance(exception, ApiException):
        if exception.status >= 500 or exception.status == 401 or exception.status == 429:
            return True
    return isinstance(exception, ClientConnectorError) and isinstance(exception.__cause__, TimeoutError)


def can_authentication_be_retried(exception: ApiException) -> bool:
    """Predicate to check if authentication call be retried,
    i.e. is an :py:class:`ApiException` with status code 429 or greater or equal to 500.
    or the exception is either a :py:cass:`TimeoutError`  (e.g. network issues)

    :param exception: The exception to be checked
    :return:
    """
    if isinstance(exception, ApiException):
        return exception.status >= 500 or exception.status == 429
    return isinstance(exception, ClientConnectorError) and isinstance(exception.__cause__, TimeoutError)


def authentication_retry(retry_state: RetryCallState):
    """Authentication retry strategy

    Retry if the raised exception verifies the can_authentication_be_retried predicate
    Raise an :py:class`AuthUnauthorizedException` if an :py:class`ApiException` with status 401 is thrown
    Raise all other exception
    """
    if retry_state.outcome.failed:
        exception = retry_state.outcome.exception()
        if can_authentication_be_retried(exception):
            return True
        if isinstance(exception, ApiException) and is_unauthorized(exception):
            unauthorized_message = "Service account is not authorized to authenticate. Check if credentials are valid. "
            raise AuthUnauthorizedError(unauthorized_message, exception) from exception
        raise exception
    return False


async def refresh_session_if_unauthorized(retry_state: RetryCallState):
    """Refreshing AuthSession tokens retry strategy


    If the call throws an :py:class`ApiException` with 401 unauthorized, we refresh the current AuthSession tokens
    and retry
    """
    if retry_state.outcome.failed:
        exception = retry_state.outcome.exception()
        if isinstance(exception, ApiException) and is_unauthorized(exception):
            service_auth_session: AuthSession = retry_state.args[0]._auth_session
            await service_auth_session.refresh()
            return True
    return False
