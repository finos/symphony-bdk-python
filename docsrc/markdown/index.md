# Symphony BDK Reference Documentation

This reference guide provides detailed information about the Symphony BDK. It provides a comprehensive documentation
for all features and abstractions made on top of the [Symphony REST API](https://developers.symphony.com/restapi/reference).

If you are just getting started with Symphony Bot developments, you may want to begin reading the
[Getting Started](./getting_started.md) guide.

The reference documentation consists of the following sections:
* [Getting Started](./getting_started.md): Introducing Symphony BDK for beginners
* [Configuration](./configuration.md): Configuration structure, formats, how to load from code
* [Authentication](./authentication.md): RSA authentication, OBO authentication
* [Message service](./message_service.md): Sending or searching messages, usage of templates
* [Stream service](./stream_service.md): Creating, searching streams, manage stream membership
* [Connection service](./connection_service.md): Managing connections between users
* [Datafeed](./datafeed.md): Listening and reacting to real-time events

### Technical Documentation
* Information on how we generate client side code from swagger specs in the
[Generated API](./tech/generated_api.md) page.
* Information about logging and logging configuration can be found in the
  [Production Readiness](./tech/production_readiness.md) page.