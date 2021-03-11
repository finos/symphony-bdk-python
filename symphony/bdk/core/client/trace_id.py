"""Module responsible for managing the trace ID sent as X-Trace-Id header and logged under the `trace_id` variable
"""
import logging
import random
import string
from contextvars import ContextVar


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
        if not DistributedTracingContext.has_trace_id():
            DistributedTracingContext.set_trace_id()

        args[4]["X-Trace-Id"] = DistributedTracingContext.get_trace_id()
        return await func(*args, **kwargs)

    return add_x_trace_id_header


class DistributedTracingContext:
    """Class to manage the tracing id context.
    """

    _trace_id_context = ContextVar("_trace_id_context")

    @classmethod
    def get_trace_id(cls):
        """Gets the current trace id.

        :return: the current trace id or empty string if not set
        """
        return cls._trace_id_context.get("")

    @classmethod
    def has_trace_id(cls):
        """Checks whether a trace id has been set.

        :return: True if a trace id has been set, False otherwise
        """
        return cls._trace_id_context.get(None) is not None

    @classmethod
    def set_trace_id(cls, trace_id: str = None):
        """Sets the trace id to a new value, either the value passed in parameter if not None
        or a newly generated value.

        :param trace_id: optional string value
        :return: None
        """
        trace_id = trace_id or cls._generate_new_trace_id()
        cls._trace_id_context.set(trace_id)

    @classmethod
    def clear(cls):
        """Clears the trace id value.

        :return: None
        """
        cls._trace_id_context.reset()

    @classmethod
    def _generate_new_trace_id(cls):
        return "".join(random.choices(string.ascii_letters + string.digits, k=6))
