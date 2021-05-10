import asyncio
import logging.config
import os
from pathlib import Path

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        datafeed_loop = bdk.datafeed()
        datafeed_loop.subscribe(RealTimeEventListenerImpl())
        await datafeed_loop.start()


class RealTimeEventListenerImpl(RealTimeEventListener):

    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        # We do not recommend logging full events in production as it could expose sensitive data
        logging.debug("Received event: %s", event)


logging.config.fileConfig(Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False)

try:
    logging.info("Running datafeed example...")
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending datafeed example")
