# Datafeed

The datafeed service is a service used for handling the [_Real Time Events_](https://docs.developers.symphony.com/building-bots-on-symphony/datafeed/real-time-events).q

When a user makes an interaction within the IM, MIM or Room chat like sending a message, joining or leaving a room chat,
when a connection request is sent, when a wall post is published or when a user replies to a Symphony element, an event
will be sent to the datafeed.

The datafeed service is a core service built on top of the Datafeed API and provides a dedicated contract to bot
developers to work with datafeed.


## How to use
The central component for the contract between bot developers and the Datafeed API is the `DatafeedLoop`.
This service is accessible from the `SymphonyBdk` object by calling the `datafeed()` method.
For instance:

```python
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener

class RealTimeEventListenerImpl(RealTimeEventListener):

    async def on_message_sent(self, initiator, event):
        # message received, interact with it
        pass

async def run():
    async with SymphonyBdk(BdkConfigLoader.load_from_symphony_dir("config.yaml")) as bdk:
        datafeed_loop = bdk.datafeed()
        datafeed_loop.subscribe(RealTimeEventListenerImpl())
        
        await datafeed_loop.start()
```

Please mind that the handling of events is done concurrently: each time an event is received and for each listener, the
datafeed loop will create a separate asyncio task. This means:
* for a given event, the corresponding listener method will run concurrently across the different listener instances.
* for a given listener instance, the listener methods will run concurrently across the different events received.

To ease the logging of event handling, a ContextVar is set with the following value:
`f"{current_task_name}/{event_id}/{listener_id}"`. It is accessible in
`symphony.bdk.core.service.datafeed.abstract_datafeed_loop.event_listener_context` can be used in logging with a filter
like:

```python
import logging

from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import event_listener_context

class EventListenerLoggingFilter(logging.Filter):
    def filter(self, record):
        record.context_id = event_listener_context.get("")
        return True

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"contextFilter": {"()": "EventListenerLoggingFilter"}},
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(context_id)s - %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
            "filters": ["contextFilter"]
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False
        }
    }
})
```