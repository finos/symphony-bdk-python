# Datafeed

The datafeed service is a service used for handling the [_Real Time Events_](https://docs.developers.symphony.com/building-bots-on-symphony/datafeed/real-time-events).

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

The overridden `RealTimeEventListener` methods *must* be `async` in order for them to be properly executed.

If a listener throws an exception, it will be logged and datafeed loop will carry on. For more information about error
handling, see [here](#error-handling)

### Concurrency of datafeed event handling

Please mind that the handling of events is done concurrently for a given chunk of events received from one read datafeed
call. For a given set of events received from one datafeed call, the datafeed loop will create separate asyncio
tasks for every event in the chunk and for every registered listener. The loop will wait for all listener tasks to
complete before making another read datafeed call.

This means, for a given received chunk of events:
* for a given event, the corresponding listener method will run concurrently across the different listener instances.
* for a given listener instance, the listener methods will run concurrently across the different events received.

If you don't want the listener calls to block the datafeed loop (i.e. having concurrency across listener calls and
across datafeed events), all listener methods must create tasks and return immediately. For instance:
```python
import asyncio
from symphony.bdk.core.activity.command import CommandActivity, CommandContext


class HelloCommandActivity(CommandActivity):

    def __init__(self):
        super().__init__()

    def matches(self, context: CommandContext) -> bool:
        return context.text_content.startswith("@" + context.bot_display_name + " /command")

    async def on_activity(self, context: CommandContext):
        # Create task to enable parallelism. Must be done for all listeners in order for the datafeed loop not to be blocked by listeners.
        asyncio.create_task(self.actual_logic(context))

    async def actual_logic(self, context):
      pass
```

### Logging
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

## Datafeed Configuration

The Datafeed Service can be configured by the datafeed field in the configuration file:

```yaml
datafeed:
  version: 'v2' # specify datafeed version 'v1' or 'v2'
  retry:
    maxAttempts: 6 # maximum number of retry attempts
    initialIntervalMillis: 2000 # initial interval between two attempts
    multiplier: 1.5 # interval multiplier after each attempt
    maxIntervalMillis: 10000 # limit of the interval between two attempts
```

For now, not all the customers have the datafeed version 2 available on their systems, that's why bot developers are able to
choose the datafeed version that they wish to use on their bot. If you want to use datafeed version 2 in your bot,  you need to set
the `version` parameter as `v2` as shown above.
Otherwise, the datafeed version 1 will be used by default.

Bot developers can also configure a dedicated retry configuration which will be used only by the datafeed service as shown above.

### Default retry configuration
By default, the Datafeed retry is configured to have an infinite number of attempts.
If no configuration is provided for Datafeed, it is equivalent to use:
```yaml
datafeed:
  retry:
    maxAttempts: -1 # infinite number of attemps
    initialIntervalMillis: 500
    multiplier: 2
    maxIntervalMillis: 300000
```

## Best practices

### Event handling

It is recommended for bot developer to make their listeners idempotent if possible or to deal with duplicated events.
When running multiple instances of a bot, this could happen if the event is slowly processed in one instance and gets
re-queued and dispatched to another instance. It can also happen that the user types a bot command twice by mistake.

Symphony also does not provide any ordering guarantees. While most of the time the events will be received in order, if
a user is very fast you might receive the second message first. In a busy room, events could be flowing in and out in
a non-chronological order.

Received events should be processed quickly (in less than 30 seconds) to avoid them being re-queued in datafeed. If the
business logic of the listener leads to long operations then it is recommended handle them in a separate asyncio task or
thread to avoid blocking the datafeed loop. To help you detect this situation, warning logs will be printed if the event
processing time exceeds 30 seconds.

Before shutting down a bot instance, you want to make sure that the datafeed loop is properly stopped and that the bot
has stopped processing events. To do so, call `datafeed.stop()` which has optional arguments `hard_kill` and `timeout`
(in seconds). `datafeed.stop()` will wait for all tasks to finish, whereas `datafeed.stop(hard_kill=False, timeout)`
will wait for `timeout` seconds before killing the tasks. `datafeed.stop(hark_kill=True)` will stop all pending or
running tasks immediately.

Stopping the datafeed loop might take a while (if the loop is currently waiting for new events, up to 30 seconds).

### Error handling

The datafeed loop once started will keep running until the bot is stopped. So it will catch all the exceptions raised by
listeners or activities to prevent the loop from stopping. However, if the processing of an event failed, and if nothing
specific is done by the listener to store it in a database or a queue, an event could be lost and never processed by the
bot.

The BDK provides a way to re-queue events if needed through the `EventError` that can be raised from listeners. In
that case the datafeed loop current execution for the currently received events will stop (other listeners will not be
called), and the events will be re-queued in datafeed. The datafeed loop will resume its execution and will after some
delays receive non-processed events (30s by default).

This feature is only available for datafeed v2. When the datafeed loop executes it can receive several events at once
and will dispatch them to all the subscribed listeners. Therefore, you should be careful about no processing an event
twice. This can be achieved by maintaining a short time lived cache of the already processed events.

### Running multiple instances of a bot (DF v2 only)

An example is provided in the
[multiple_instances](https://github.com/finos/symphony-bdk-python/tree/main/examples/multiple_instances)
folder.

With datafeed v2 it is possible to run multiple instances of a bot. Each instance will receive events in turn. The
examples also makes use of Hazelcast to keep a distributed cache of already processed events and avoid replying to a
message twice.

The logic to avoid handling an event twice is tied to the bot and its logic so the BDK makes no assumption about it and
lets you manage it freely.
