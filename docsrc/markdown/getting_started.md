# Getting started with Symphony BDK for Python

This guide provides detailed information for beginners who want to bootstrap their first Symphony BDK project
in Python. The Symphony BDK requires **Python 3.8 or higher**.

## Starting with Symphony Generator
> This section requires `npm` ([Node Package Manager](https://www.npmjs.com/)) to be installed on your local machine as a prerequisite

For all Symphony BDK applications, you should start with the [Symphony Generator](https://github.com/finos/generator-symphony).
The Symphony Generator offers a fast way to bootstrap your Symphony BDK project in several languages, including Python:
```
npm i -g @finos/generator-symphony
yo @finos/symphony
```
After entering pod and bot information and selecting `Bot Application` as application type, you should be able to select
Python as programming language. This will generated a configuration file, a `requirements.txt` and a simple python script.

## Creating your project _from scratch_
This section will help you to understand how to create your bot application from scratch.

### Setuptools based project (setup.py + requirements.txt)
If you want to use setuptools, please configure your `setup.py` as follows:
```python
from setuptools import setup

setup(
    name='botproject',
    version='0.0.1',
    packages=['mypackage'],
    url='',
    license='MIT',
    author='jane.doe',
    author_email='jane.doe@acme.com',
    description='My Python bot',
    python_requires='>=3.8',
    install_requires=['symphony-bdk-python>=2.0.0']
)

```
and your `requirements.txt` like:
```
symphony-bdk-python>=2.0.0
```

### Poetry based project
If you want to use [poetry](https://python-poetry.org/) as a build system, please configure your `pyproject.toml` as follows:
```toml
[tool.poetry]
name = "my_bot"
version = "0.1.0"
description = "My bot"

[tool.poetry.dependencies]
python = "^3.8"
symphony-bdk-python = "^2.0.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

You can then run your script by running `poetry run python main.py`

### Create configuration file
Before implement any code, you need to create your `~/.symphony/config.yaml` configuration file according
to your Symphony environment:
```yaml
host: acme.symphony.com                       # your own pod host name

bot:
    username: bot-username                    # your bot (or service account) username
    privateKey:
      path: /path/to/bot/rsa-private-key.pem  # your bot RSA private key
```
> Click [here](./configuration.md) for more detailed documentation about BDK configuration

### Create a Simple Bot Application
Now you can create a Simple Bot Application by creating a main script:

```python
async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        datafeed_loop = bdk.datafeed()
        datafeed_loop.subscribe(RealTimeEventListenerImpl(bdk.messages()))
        await datafeed_loop.start()


class RealTimeEventListenerImpl(RealTimeEventListener):

    def __init__(self, message_service):
        self._message_service = message_service

    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        await self._message_service.send_message(event.message.stream.stream_id,
                                                 f"<messageML>Hello, {initiator.user.display_name}!</messageML>")


try:
    logging.info("Running datafeed example...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending datafeed example")
```
1. The `SymphonyBdk` class acts as an entry point into the library and provides an API to access
to the main BDK features such as [Datafeed](./datafeed.md), [Datahose](./datafeed.md#datahose) or [message service](./message_service.md).
2. Subscribe to the [`on_message_sent`](https://docs.developers.symphony.com/building-bots-on-symphony/datafeed/real-time-events#message-sent)
[Real Time Event](https://docs.developers.symphony.com/building-bots-on-symphony/datafeed/real-time-events)
3. When any message is sent into a stream where your bot is a member, it will reply with a hello message.
4. Start the Datafeed read loop
