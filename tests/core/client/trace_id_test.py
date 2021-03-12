from symphony.bdk.core.client.trace_id import DistributedTracingContext


def setup_function(function):
    DistributedTracingContext.clear()


def test_empty_tracing_context():
    assert not DistributedTracingContext.has_trace_id()
    assert DistributedTracingContext.get_trace_id() == ""
    assert not DistributedTracingContext.is_trace_id_set_by_user()


def test_set_trace_id():
    trace_id = "trace-id"
    DistributedTracingContext.set_trace_id(trace_id)

    assert DistributedTracingContext.has_trace_id()
    assert DistributedTracingContext.get_trace_id() == trace_id
    assert DistributedTracingContext.is_trace_id_set_by_user()


def test_set_new_trace_id():
    DistributedTracingContext.set_new_trace_id()

    assert DistributedTracingContext.has_trace_id()
    assert DistributedTracingContext.get_trace_id() != ""
    assert not DistributedTracingContext.is_trace_id_set_by_user()


def test_clear_trace_id():
    DistributedTracingContext.set_trace_id("trace-id")
    DistributedTracingContext.clear()

    assert not DistributedTracingContext.has_trace_id()
    assert DistributedTracingContext.get_trace_id() == ""
    assert not DistributedTracingContext.is_trace_id_set_by_user()
