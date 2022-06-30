# Activity API

The Activity API is an abstraction built on top of the Datafeed's [_Real Time Events_](https://docs.developers.symphony.com/building-bots-on-symphony/datafeed/real-time-events).
An Activity is basically a user interaction triggered from the chat.
Two different kinds of activities are supported by the BDK:
- **Command Activity**: triggered when a message is sent in an `IM`, `MIM` or `Chatroom`
- **Form Activity**: triggered when a user replies to an [_Elements_](https://docs.developers.symphony.com/building-bots-on-symphony/symphony-elements)
  form message
- **User Joined Room Activity**: triggered when a user joins a room in which the bot is a member

---
**NOTE**

Please note that all callback methods *must* be `async` in order for them to be executed, namely:
* the callback methods decorated with `@slash`
* the `on_activity` methods for all activities

---

## Activity Registry
The central component for activities is the
[`ActivityRegistry`](../_autosummary/symphony.bdk.core.activity.registry.ActivityRegistry.html).
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
    bdk.activities().register(HelloCommandActivity(bdk.messages()))
    await bdk.datafeed().start()


class HelloCommandActivity(CommandActivity):

  def __init__(self, messages: MessageService):
    self._messages = messages
    super().__init__()
  
  def matches(self, context: CommandContext) -> bool:
     return context.text_content.startswith("@" + context.bot_display_name + " /hello") # (1)
  
  async def on_activity(self, context: CommandContext):
      await self._messages.send_message(context.stream_id, "<messageML>Hello, World!</messageML>") # (2)


logging.config.fileConfig(os.path.dirname(os.path.abspath(__file__)) + '/logging.conf', disable_existing_loggers=False)

try:
    logging.info("Running activity example...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending activity example")
```
1. The `matches()` method allows the activity logic to be triggered when a message starts by a mention to the bot and the text `/hello` separated by a space. Ex: `@bot_name /hello`
2. The activity logic. Here, we send a message: "Hello, World"

### Slash Command
A _Slash_ command can be used to directly define a very simple bot command such as: 
```
$ @BotMention /command
$ /command
$ /command string_argument #hashtag_argument
$ /command $cashtag_argument @user_mention_argument
```

> Note: a Slash can have parameters as String, Cashtag, Hashtag and Mention

#### With the @slash decorator
One can define a slash command by decorating a callback function which must take one parameter of type
[`CommandContext`](../_autosummary/symphony.bdk.core.activity.command.CommandContext.html)
such as below:

```python
import logging

from symphony.bdk.core.activity.command import CommandContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk

async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        activities = bdk.activities()

        @activities.slash("/hello",                     # (1)
                          True,                         # (2)
                          "This command says hello")    # (3)
        async def callback(context: CommandContext):
            logging.debug("Hello slash command triggered by user %s", context.initiator.user.display_name)

        await bdk.datafeed().start()
```
1. `/hello` is the command name 
2. `True` means that the bot has to be mentioned (optional, True is the default)
3. `This command says hello` is the command description (optional)

The decorated function will then be called if a message is sent in an `IM`, `MIM` or `Chatroom` with a matching text message.
Please mind that, due to the mechanism inherent to decorators, the `@activities.slash` cannot be used when `activities`
is a class instance field. In this case, you can use slash commands as done below by subclassing `SlashCommandActivity`.

#### By subclassing SlashCommandActivity
One can also define a slash command by hand like the following:
```python
from symphony.bdk.core.activity.command import CommandContext, SlashCommandActivity
from symphony.bdk.core.activity.registry import ActivityRegistry
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.symphony_bdk import SymphonyBdk

async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        activities = bdk.activities()
        messages = bdk.messages()

        activities.register(HelpCommandActivity(messages, activities))

        await bdk.datafeed().start()


class HelpCommandActivity(SlashCommandActivity):

    def __init__(self, messages: MessageService, activities: ActivityRegistry):
        self._messages = messages
        self._activities = activities
        super().__init__("/help", True, self.help_command)

    async def help_command(self, context: CommandContext):
        return await self._messages.send_message(context.stream_id, "<messageML>Help command triggered</messageML>")
```

#### Slash command pattern format
The slash command can be a simple static pattern without arguments, like `/command` or `/command help`.
You may specify one or more arguments by enclosing them with braces like `{myArgument}`.
The string inside the braces must have at least one character and must not have whitespaces.
If there are some arguments, each argument is mandatory in order for the slash command to be triggered. For instance:
* for command pattern `/command {arg}`:
  * `/command` won't match
  * `command help` will match
  * `command help me` won't match

Arguments can be of several types:
* `{wordArgument}` will match a regular word only (won't match a mention, a cashtag or a hashtag)
* `{@mentionArgument}` will match a mention only
* `{#hastagArgument}` will match a hashtag only
* `{$cashtagArgument}` will match a cashtag only

In the slash command definition, each argument must be separated by a whitespace to be valid. For instance:
* `{arg1} {@arg2}` is valid
* `{arg1}{arg2}` is invalid

Argument names must be unique inside a given pattern.
* `/command {arg1} {@arg1} {#arg1}` is an invalid pattern.

When a slash command matches, arguments can be retrieved thanks to the `arguments` field in the `CommandContext` object.
Available functions to handle arguments:
* context.arguments.get_argument_names(): Lists all arguments keys
* context.arguments.get(key: str): Returns the argument value. None if not found.
* context.arguments.get_string(key: str), get_hashtag(key: str), get_cashtag(key: str), get_mention(key: str): Returns the argument value. None if not found or if the type is not correct.
* context.arguments.get_as_string(key: str): Returns the argument value as a String. None if not found.

Example of a slash command with arguments:
```python
from symphony.bdk.core.activity.command import CommandContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    async with SymphonyBdk(BdkConfigLoader.load_from_symphony_dir("config.yaml")) as bdk:
        activities = bdk.activities()
        messages = bdk.messages()

        @activities.slash("/buy {$ticker} {quantity}")
        async def on_echo_mention(context: CommandContext):
            ticker = context.arguments.get_cashtag("ticker").value # can also be retrieved with context.arguments.get("ticker").value
            quantity = context.arguments.get_string("quantity")
            
            message = f"Buy ticker {ticker} with quantity {quantity}"

            await messages.send_message(context.stream_id, f"<messageML>{message}</messageML>")
```

### Help Command
The _help_ command is a BDK build-in command which lists all the commands registered in the ActivityRegistry of the BDK. 
It can be triggered by using:
```
$ @BotMention /help
```
The help command can be instantiated by passing a `SymphonyBdk` instance to the constructor and then added manually to the BDK activity registry
```python
import logging
from symphony.bdk.core.activity.command import CommandContext
from symphony.bdk.core.activity.help_command import HelpCommand
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    
    async with SymphonyBdk(config) as bdk:
        activities = bdk.activities()
        
        @activities.slash("/hello", True, "Command to say hello")
        async def callback(context: CommandContext):
            logging.debug("Hello slash command triggered by user %s", context.initiator.user.display_name)
        
        bdk.activities().register(HelpCommand(bdk))
        
        await bdk.datafeed().start()
```
One can also override the default implementation of the help command by manually defining a new `SlashCommandActivity`.

## Form Activity
A form activity is triggered when an end-user replies or submits an Elements form.

### How to create a Form Activity
For this example, we will assume that the following Elements form has been posted into a room: 
```xml
<messageML>
    <h2>Hello Form</h2>
    <form id="hello-form"> <!-- (1) -->

        <text-field name="name" placeholder="Enter a name here..."/> <!-- (2) -->

        <button name="submit" type="action">Submit</button> <!-- (3) -->
        <button type="reset">Reset Data</button>

    </form>
</messageML>
```
1. the formId is "**hello-form**"
2. the form has one unique `<text-field>` called "**name**"
3. the has one action button called "**submit**"

The following code example handles the above form submission:
```Python
import asyncio
import logging.config
from pathlib import Path

from symphony.bdk.core.activity.form import FormReplyActivity, FormReplyContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    async with SymphonyBdk(BdkConfigLoader.load_from_symphony_dir("config.yaml")) as bdk:
        bdk.activities().register(ReplyFormReplyActivity(bdk.messages()))
        await bdk.datafeed().start()


class ReplyFormReplyActivity(FormReplyActivity):
    def __init__(self, messages: MessageService):
        self.messages = messages

    def matches(self, context: FormReplyContext) -> bool:
        return context.form_id == "hello-form" \ 
               and context.get_form_value("action") == "submit" # (1)

    async def on_activity(self, context: FormReplyContext):
        message = "Hello, " + context.getFormValue("name") + "!" # (2)
        await self.messages.send_message(context.source_event.stream.stream_id,
                                         "<messageML>" + message + "</messageML>") # (3)

        
logging.config.fileConfig(Path("../logging.conf"), disable_existing_loggers=False)

try:
    logging.info("Running activity example...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending activity example")
```
1. The `matches()` method allows the activity logic to be triggered when a form with the `id` `"hello-form"` has been submitted from the action button `"submit"`
2. The activity context allows us to retrieve form values. Here, the content of the `<text-field>` called "**name**"
3. We send back the message: "Hello, **text_field_content**"

## User Joined Room Activity

A User Joined Room activity is triggered when a new user joins or is added to a room in which the bot service account is
a member, including when the bot service account joins or is added to a room.

The code sample below shows how to create such an activity:
```python
from symphony.bdk.core.activity.user_joined_room import UserJoinedRoomActivity, UserJoinedRoomContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    async with SymphonyBdk(BdkConfigLoader.load_from_symphony_dir("config.yaml")) as bdk:
        bdk.activities().register(JoinRoomActivity(bdk.messages()))
        await bdk.datafeed().start()


class JoinRoomActivity(UserJoinedRoomActivity):
    def __init__(self, messages: MessageService):
        self._messages = messages
        super().__init__()

    def matches(self, context: UserJoinedRoomContext) -> bool:
        return True

    async def on_activity(self, context: UserJoinedRoomContext):
        await self._messages.send_message(context.stream_id,
                                          f"<messageML>Welcome to the room {context.affected_user_id}!</messageML>")
```

---
**NOTE - General activities use case**

For you to not overload your matches method, you can pre-process a context before the `matches()` method is called by
overriding the `before_matcher()` method of any activity.
```Python
class DummyActivityExample(CommandActivity):
    
    def matches(self, context: CommandContext) -> bool:
        return context.some_attribute == "some_value"
    
    async def on_activity(self, context: CommandContext):
        # Do stuff

    def before_matcher(self, context: CommandContext):
        context.some_attribute = some_call_to_another_service()
```
