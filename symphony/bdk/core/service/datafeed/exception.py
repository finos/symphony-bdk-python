class EventError(Exception):
    """A particular exception to throw from
    :py:class:`~symphony.bdk.core.service.datafeed.real_time_event_listener.RealTimeEventListener` implementations
    to explicitly indicate that the event processing has failed and that all the events received in
    the datafeed read events call should be re-queued.
    They will eventually get redispatched after some time (30s by default). Only supported by DFv2.
    """
