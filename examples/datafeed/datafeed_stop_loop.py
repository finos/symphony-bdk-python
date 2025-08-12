import asyncio
import logging.config

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import event_listener_context
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        datafeed_loop = bdk.datafeed()
        datafeed_loop.subscribe(RealTimeEventListenerImpl())

        t = asyncio.create_task(datafeed_loop.start())  # start DF loop

        await asyncio.sleep(10)
        await datafeed_loop.stop()  # stop after 10s

        await t  # wait for DF loop to finish


class RealTimeEventListenerImpl(RealTimeEventListener):
    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        logging.debug("Received event: %s", event.message.message_id)
        await asyncio.sleep(5)
        with open("events.txt", "a") as file:
            file.write(f"{event.message.message_id}\n")
        logging.debug("After event: %s", event.message.message_id)


# This is to show how to log the event_listener_context in each log line
class EventListenerLoggingFilter(logging.Filter):
    def filter(self, record):
        record.context_id = event_listener_context.get("")
        return True


logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {"contextFilter": {"()": "__main__.EventListenerLoggingFilter"}},
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
                "filters": ["contextFilter"],
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["default"],
                "level": "DEBUG",
                "propagate": False,
            }
        },
    }
)

try:
    logging.info("Running datafeed example...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending datafeed example")
