# Activity API

The Activity API is an abstraction built on top of the Datafeed's [_Real Time Events_](https://developers.symphony.com/restapi/docs/real-time-events). An Activity is basically a user interaction triggered from the chat.
Two different kinds of activities are supported by the BDK:
- **Command Activity**: triggered when a message is sent in an `IM`, `MIM` or `Chatroom`
- **Form Activity**: triggered when a user replies to an [_Elements_](https://developers.symphony.com/symphony-developer/docs/overview-of-symphony-elements) form message

## Activity Registry
The central component for activities is the [`ActivityRegistry`](../../symphony/bdk/core/activity/registry.py).
This component is used to either add or retrieve activities. It is accessible from the `SymphonyBdk` object.

```python
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.core.config.loader import BdkConfigLoader

async def run():
  async with SymphonyBdk(BdkConfigLoader.load_from_symphony_dir("config.yaml")) as bdk:
    activity_registry = bdk.activities()
```

## Command Activity
A command activity is triggered when a message is sent in an `IM`, `MIM` or `Chatroom`. This is the most basic interaction 
between an end-user and the bot. Here are some command activity examples: 

- the bot is mentioned followed by a _slash_ command:
```
$ @BotMention /buy
```
- a command with parameters, the bot is not mentioned:
```
$ /buy 1000 goog
```
- any message that contains 'hello' can be a command:
```
$ I want to say hello to the world
```

### How to create a Command Activity

```python
import asyncio
import logging.config
import os

from symphony.bdk.core.activity.command import CommandActivity, CommandContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
  async with SymphonyBdk(BdkConfigLoader.load_from_symphony_dir("config.yaml")) as bdk:
    await bdk.activities().register(HelloCommandActivity(bdk.messages()))
    await bdk.datafeed().start()


class HelloCommandActivity(CommandActivity):

  def __init__(self, messages: MessageService):
    self._messages = messages
    super().__init__()
  
  def matches(self, context: CommandContext) -> bool:
     return context.text_content.startswith("@" + context.bot_display_name + " /hello")
  
  async def on_activity(self, context: CommandContext):
      await self._messages.send_message(context.stream_id, "<messageML>Hello, World!</messageML>")


logging.config.fileConfig(os.path.dirname(os.path.abspath(__file__)) + '/logging.conf', disable_existing_loggers=False)

try:
    logging.info("Running activity example...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending activity example")
```
