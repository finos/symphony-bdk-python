"""Module responsible for managing the trace ID sent as X-Trace-Id header and logged under the `trace_id` variable
"""
import logging
import random
import string
from contextvars import ContextVar

TRACE_ID_LENGTH = 6

X_TRACE_ID = "X-Trace-Id"

HEADER_ARG_INDEX = 4


def setup_trace_id_log_record_factory():
    """Adds the `trace_id` variable to the log records.

    :return: the updated log record factory which adds the `trace_id` variable with the current trace id value
    """
    old_factory = logging.getLogRecordFactory()

    def trace_id_log_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.trace_id = DistributedTracingContext.get_trace_id()

        return record

    logging.setLogRecordFactory(trace_id_log_factory)


def add_x_trace_id(func):
    """Decorator of ApiClient.__call_api function so that it adds the `X-Trace-Id` header
    with the current trace id value to the HTTP call.

    :param func: the function to be decorated
    :return: the decorated function
    """

    async def add_x_trace_id_header(*args, **kwargs):
        if not DistributedTracingContext.is_trace_id_set_by_user():
            DistributedTracingContext.set_new_trace_id()

        if DistributedTracingContext.has_trace_id() and len(args) > HEADER_ARG_INDEX:
            args[HEADER_ARG_INDEX][X_TRACE_ID] = DistributedTracingContext.get_trace_id()

        return await func(*args, **kwargs)

    return add_x_trace_id_header


class DistributedTracingContext:
    """Class to manage the tracing id context.
    """

    _trace_id_context = ContextVar("_trace_id_context")
    _is_trace_id_set_by_user = False

    @classmethod
    def get_trace_id(cls) -> str:
        """Gets the current trace id.

        :return: the current trace id or empty string if not set
        """
        return cls._trace_id_context.get("")

    @classmethod
    def has_trace_id(cls) -> bool:
        """Checks whether a trace id has been set.

        :return: True if a trace id has been set, False otherwise
        """
        return cls.get_trace_id() != ""

    @classmethod
    def is_trace_id_set_by_user(cls) -> bool:
        """Checks whether the trace id has been manually set using :func:`~set_trace_id`.

        :return: True if a trace id has been manually set, False otherwise
        """
        return cls._is_trace_id_set_by_user

    @classmethod
    def set_trace_id(cls, trace_id: str) -> None:
        """Sets the trace id to a new value.

        :param trace_id: string value, should not be None or empty
        :return: None
        """
        cls._trace_id_context.set(trace_id)
        cls._is_trace_id_set_by_user = True

    @classmethod
    def set_new_trace_id(cls) -> None:
        """Sets the trace id to a newly generated value.

        :return: None
        """
        trace_id = "".join(random.choices(string.ascii_letters + string.digits, k=TRACE_ID_LENGTH))
        cls._trace_id_context.set(trace_id)

    @classmethod
    def clear(cls) -> None:
        """Clears the trace id value.

        :return: None
        """
        cls._trace_id_context.set("")
        cls._is_trace_id_set_by_user = False
