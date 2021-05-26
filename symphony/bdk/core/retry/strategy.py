from aiohttp import ClientConnectorError
from tenacity import RetryCallState

from symphony.bdk.core.auth.exception import AuthUnauthorizedError
from symphony.bdk.gen import ApiException


def is_unauthorized(exception: Exception) -> bool:
    return isinstance(exception, ApiException) and exception.status == 401


def is_client_error(exception: Exception) -> bool:
    return isinstance(exception, ApiException) and exception.status == 400


def is_client_timeout_error(exception: Exception):
    """Checks if the exception is a :py:class:`ClientConnectorError` with a :py:class:`TimeoutError` as cause

    :param exception: The exception to be checked
    :return: True if checks the predicate, False otherwise
    """
    return isinstance(exception, ClientConnectorError) and isinstance(exception.__cause__, TimeoutError)


def can_authentication_be_retried(exception: Exception) -> bool:
    """Checks if the exception is a network issue or internal or retry error
    i.e. is an :py:class:`ApiException` with status code 429 or greater or equal to 500.
    or the exception is either a :py:class:`TimeoutError`  (e.g. network issues)

    :param exception: The exception to be checked
    :return: True if the exception is an :py:class:`ApiException` with status 500, 429 or or is a client timeout error
             False otherwise
    """
    if isinstance(exception, ApiException):
        return exception.status >= 500 or exception.status == 429
    return is_client_timeout_error(exception)


def _is_minor_error(exception: ApiException):
    return exception.status >= 500 or exception.status == 401 or exception.status == 429


def is_network_or_minor_error(exception: Exception) -> bool:
    """Checks if the exception is a network issue or an :py:class:`ApiException` minor error (internal +
    unauthorized + retry). This is the default function used to check if a given exception should lead to a retry.

    :param exception: The exception to be checked
    :return: True if the exception is an :py:class:`ApiException` with status 500, 401, 429 or is a client timeout error
             False otherwise
    """
    if isinstance(exception, ApiException):
        return _is_minor_error(exception)
    return is_client_timeout_error(exception)


def is_network_or_minor_error_or_client(exception: Exception) -> bool:
    """Checks if the exception is a network issue or an :py:class:`ApiException` minor error or a client error

    :param exception: The exception to be checked
    :return: True if the exception is an :py:class:`ApiException` with status 500, 401, 429, 400
             or is a client timeout error False otherwise
    """
    if isinstance(exception, ApiException):
        return _is_minor_error(exception) or exception.status == 400
    return is_client_timeout_error(exception)


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
        if is_unauthorized(exception):
            unauthorized_message = "Service account is not authorized to authenticate. Check if credentials are valid. "
            raise AuthUnauthorizedError(unauthorized_message, exception) from exception
        raise exception
    return False


async def refresh_session_if_unauthorized(retry_state: RetryCallState):
    """Refreshing AuthSession tokens retry strategy

    Retry if the raised exception verifies the is_network_or_minor_error predicate
    If this exception is a 401 unauthorized error, we refresh the current AuthSession tokens
    """
    if retry_state.outcome.failed:
        exception = retry_state.outcome.exception()
        if is_network_or_minor_error(exception):
            if is_unauthorized(exception):
                service_auth_session = retry_state.args[0]._auth_session
                await service_auth_session.refresh()
            return True
    return False


async def read_datafeed_retry(retry_state: RetryCallState):
    """Read datafeed retry strategy

    Retry if the raised exception verifies the is_network_or_minor_error_or_client predicate
    If this exception is a 400 client error, we recreate the datafeed
    If this exception is a 401 unauthorized error, we refresh the current AuthSession tokens
    """
    if retry_state.outcome.failed:
        exception = retry_state.outcome.exception()
        if is_network_or_minor_error_or_client(exception):
            if is_client_error(exception):
                datafeed_service = retry_state.args[0]  # datafeed_service is an AbstractDataFeedLoop instance
                await datafeed_service.recreate_datafeed()
            elif is_unauthorized(exception):
                service_auth_session = retry_state.args[0]._auth_session
                await service_auth_session.refresh()
            return True
        raise exception
    return False
