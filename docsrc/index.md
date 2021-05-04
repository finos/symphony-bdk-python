Contents
--------

* [Getting Started](markdown/getting_started.md)
* [Configuration](markdown/configuration.md)
* [Authentication](markdown/authentication.md)
* [Datafeed](markdown/datafeed.md)
* [Activity API](markdown/activity-api.md)
* [Message service](markdown/message_service.md)
* [Stream service](markdown/stream_service.md)
* [Connection service](markdown/connection_service.md)
* [Application service](markdown/application_service.md)
* [Signal service](markdown/signal_service.md)
* [Presence service](markdown/presence_service.md)
* [FAQ](markdown/faq.md)

```eval_rst
.. autosummary::
   :toctree: _autosummary
   :template: custom-module-template.rst
   :recursive:

   symphony.bdk.core
```

# Symphony BDK Reference Documentation

This reference guide provides detailed information about the
[Symphony BDK](https://github.com/SymphonyPlatformSolutions/symphony-api-client-python/tree/2.0).
It provides a comprehensive documentation for all features and abstractions made on top of the
[Symphony REST API](https://developers.symphony.com/restapi/reference).

If you are just getting started with Symphony Bot developments, you may want to begin reading the
[Getting Started](markdown/getting_started.md) guide.

The reference documentation consists of the following sections:
* [Getting Started](markdown/getting_started.md): Introducing Symphony BDK for beginners
* [Configuration](markdown/configuration.md): Configuration structure, formats, how to load from code
* [Authentication](markdown/authentication.md): RSA authentication, OBO authentication
* [Datafeed](markdown/datafeed.md): Listening and reacting to real-time events
* [Activity API](markdown/activity-api.md): Abstraction on top of the datafeed loop to ease consumption of datafeed events
* Services:
  * [Message service](markdown/message_service.md): Sending or searching messages, usage of templates
  * [Stream service](markdown/stream_service.md): Creating, searching streams, manage stream membership
  * [Connection service](markdown/connection_service.md): Managing connections between users
  * [Signal service](markdown/signal_service.md): Managing signals, subscribing/unsubscribing to signals
  * [Presence service](markdown/presence_service.md): Reacting and managing presences

### Technical Documentation
* Information on how we generate client side code from swagger specs in the
[Generated API](markdown/tech/generated_api.md) page.
* Information about logging and logging configuration can be found in the
  [Production Readiness](markdown/tech/production_readiness.md) page.

Indices and tables
------------------

```eval_rst
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```
