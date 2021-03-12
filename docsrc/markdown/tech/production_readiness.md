# Production Readiness
Production readiness documentation for BDK-based applications.

## Logging

The Symphony BDK uses
the [standard Python logging module](https://docs.python.org/3/howto/logging.html). To troubleshoot
your bot you might want to enable the DEBUG level to get the full logs from the BDK.
The [Datafeed example](https://github.com/SymphonyPlatformSolutions/symphony-api-client-python/blob/2.0/examples/datafeed.py) uses
a [sample logging configuration](https://github.com/SymphonyPlatformSolutions/symphony-api-client-python/blob/2.0/examples/logging.conf)
and illustrates how you can configure logging as a bot developer.

If you are logging to a file we recommend that you use
a [rotating file handler](https://docs.python.org/3/library/logging.handlers.html#logging.handlers.RotatingFileHandler)
to avoid filling the disk.

**Beware of logging sensitive or personal data such as message content, user details,...**

### X-Trace-Id
The Symphony BDK adds a `trace_id` field to each log record with a value called `X-Trace-Id`
(random alphanumeric string of 6 characters).
You are free to print it in your logs using pattern `%(trace-id)s` using a suitable logformat string, for instance like
done in the
[sample logging configuration](https://github.com/SymphonyPlatformSolutions/symphony-api-client-python/blob/2.0/examples/logging.conf).

This value is send as header of every request made to the Symphony API. This is especially useful for cross-applications
debugging, assuming that the `X-Trace-Id` value is also present in your application logs. A new value is generated for
each request made to the Symphony API, except if you decide to set a custom value using
[DistributedTracingContext](../../_autosummary/symphony.bdk.core.client.trace_id.DistributedTracingContext).
In this case, you will have to manage the `X-Trace-Id` yourself and no new value will be generated.
