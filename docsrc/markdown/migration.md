# Migration guide to Symphony BDK 2.0

This guide provides information about how to migrate from Symphony BDK 1.0 to BDK 2.0. Migration for the following topics will be detailed here:
- Dependencies
- Bot configuration
- Symphony BDK entry point
- BDK services
- Event listeners

## Dependencies
To use the Python BDK 1.x, you had to use the
[`sym-api-client-python` Pypi package](https://pypi.org/project/sym-api-client-python/) in your `requirements.txt` file.
For the Python BDK 2.0, package name has been changed to [`symphony-bdk-python`](https://pypi.org/project/symphony-bdk-python/).

## Bot configuration
In order for bots to function, a configuration file is needed. Whereas Python BDK 1.x only supports JSON format,
Python BDK 2.0 supports both JSON and YAML formats.

Bot configuration for Python BDK 2.0 should have the following properties:
- `host`: pod host name
- `bot.username`: bot (or service account) username
- `bot.privatekey.path`: path to bot private key file

If your bot is deployed on premise, the following properties are required as well:
- `agent`: on premise agent configuration
- `keyManager`: on premise Key manager configuration
- `proxy`: proxy configuration to reach the pod
- `ssl.trustStore.path`: path to truststore file in PEM format

> Click [here](./configuration.md) for more detailed documentation about BDK configuration.

### Minimal configuration example

#### Python BDK 1.x
```json
{
    "sessionAuthHost": "acme.symphony.com",
    "keyAuthHost": "acme.symphony.com",
    "podHost": "acme.symphony.com",
    "agentHost": "acme.symphony.com",
    "botUsername": "bot-username",
    "botPrivateKeyPath": "/folder/to/private/key/",
    "botPrivateKeyName": "rsa-privatekey.pem",
    "truststorePath": ""
}
```

### Python BDK 2.0
In JSON:
```json
{
    "host": "acme.symphony.com",
    "bot": {
        "username": "bot-username",
        "privateKey": {
            "path": "/folder/to/private/key/rsa-privatekey.pem"
        }
    }
}
```
Or in YAML:
```yaml
host: acme.symphony.com
bot:
    username: bot-username
    privateKey:
        path: "/folder/to/private/key/rsa-privatekey.pem"
```

## Symphony BDK entry point

For the BDK 1.x, `SymBotClient` object acts as an entry point for all services, whereas for the BDK 2.0, it is the `SymphonyBdk` object.
Whereas the BDK 1.x exposes synchronous methods, the BDK 2.0 exposes most of the service methods as `async` methods.
Therefore, an `asyncio` loop is needed to use the BDK.

Please check below for examples or check the [getting started](./getting_started.md) guide.

## BDK services
To illustrate the use of services, let's take an example of a bot reacting to *ping pong* messages.

### Using the BDK 1.x

```python
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.configure.configure import SymConfig
from sym_api_client_python.listeners.im_listener import IMListener
from sym_api_client_python.processors.sym_message_parser import SymMessageParser


class PingPongListener(IMListener):
    def __init__(self, sym_bot_client):
        self.bot_client = sym_bot_client
        self.message_parser = SymMessageParser()

    def on_im_message(self, im_message):
        stream_id = self.message_parser.get_stream_id(im_message)
        message_text = self.message_parser.get_text(im_message)[0]

        if message_text == "/ping":
            self._send_message(stream_id, "<messageML>pong</messageML>")
        elif message_text == "/pong":
            self._send_message(stream_id, "<messageML>ping</messageML>")
        else:
            self._send_message(stream_id, "<messageML>Sorry, I don't understand!</messageML>")

    def on_im_created(self, im_created):
        pass

    def _send_message(self, stream_id, message):
        self.bot_client.get_message_client().send_msg(stream_id, dict(message=message))


def main():
    # Load configuration
    configure = SymConfig('../resources/config.json')
    configure.load_config()

    # authenticate
    auth = SymBotRSAAuth(configure)
    auth.authenticate()

    bot_client = SymBotClient(auth, configure)

    datafeed_event_service = bot_client.get_datafeed_event_service()
    datafeed_event_service.add_im_listener(PingPongListener(bot_client))

    print('Starting datafeed')
    try:
        datafeed_event_service.start_datafeed()
    except (KeyboardInterrupt, SystemExit):
        print('Stopping datafeed')


if __name__ == "__main__":
    main()
```

### Using the BDK 2.0

```python
import asyncio

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.service.message.message_parser import get_text_content_from_message
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent


class PingPongListener(RealTimeEventListener):

    def __init__(self, message_service):
        self._message_service = message_service

    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        message_text = get_text_content_from_message(event.message)
        stream_id = event.message.stream.stream_id
        if message_text == "/ping":
            await self._message_service.send_message(stream_id=stream_id, message="<messageML>pong</messageML>")
        elif message_text == "/pong":
            await self._message_service.send_message(stream_id=stream_id, message="<messageML>ping</messageML>")
        else:
            await self._message_service.send_message(stream_id=stream_id,
                                                     message="<messageML>Sorry, I don't understand!</messageML>")


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        datafeed_loop = bdk.datafeed()
        datafeed_loop.subscribe(PingPongListener(bdk.messages()))
        await datafeed_loop.start()


if __name__ == "__main__":
    try:
        print("Running datafeed example...")
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Ending datafeed example")
```

## Event listeners

### Python BDK 1.x
In the Python BDK 1.x, we have three main types of listeners:
- for IM (1 to 1 conversation)
- for MIM (room)
- for Symphony elements

There are also listener types for:
- for connection requests
- for wall posts
- for message suppression

See [datafeed_event_service](https://github.com/finos/symphony-bdk-python/blob/legacy/sym_api_client_python/datafeed_event_service.py) for more details.

### Python BDK 2.0
In the Python BDK 2.0, we have a `RealTimeEventListener` type that listens to all events. Only events you are interested
in needs to have the corresponding method overridden. See [datafeed](./datafeed.md) documentation for more information.

The BDK 2.0 also provides a simple way to listen for `MESSAGESENT` events thanks to activities.
See the [dedicated page](./activity-api.md) on how to use it.

## Models
Models names have been changed in Python BDK 2.0. They actually follow the models in the openapi specification of
[Symphony's public API](https://github.com/symphonyoss/symphony-api-spec). Field names in Python classes correspond to
the field names in API's JSON payloads. This requires to change some variable types in your legacy bots.

Whereas most of the objects used in the Python BDK 1.x are Python dictionaries, the Python BDK 2.0 leverages objects
generated from the openapi specifications. All public methods exposed by the BDK have type hints so that you can easily
know which types are used as parameters or returned. You can also check the generated documentation [here](../_autosummary/symphony.bdk.core.html).
