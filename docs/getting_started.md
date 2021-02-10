# Getting started

## Logging

The Symphony BDK uses
the [standard Python logging module](https://docs.python.org/3/howto/logging.html). To troubleshoot
your bot you might want to enable the DEBUG level to get the full logs from the BDK.
The [Datafeed example](../examples/datafeed.py) uses
a [sample logging configuration](../examples/logging.conf)
and illustrates how you can configure logging as a bot developer.

If you are logging to a file we recommend that you use
a [rotating file handler](https://docs.python.org/3/library/logging.handlers.html#logging.handlers.RotatingFileHandler)
to avoid filling the disk.

**Beware of logging sensitive or personal data such as message content, user details,...**
