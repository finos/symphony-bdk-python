import asyncio
import logging.config
from pathlib import Path

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_instant_message_created import V4InstantMessageCreated
from symphony.bdk.gen.agent_model.v4_message_suppressed import V4MessageSuppressed
from symphony.bdk.gen.agent_model.v4_room_updated import V4RoomUpdated
from symphony.bdk.gen.agent_model.v4_room_created import V4RoomCreated
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent


async def run():
    config = BdkConfigLoader.load_from_file("/Users/soufiane/.symphony/rsa-devx3/config.yaml")

    async with SymphonyBdk(config) as bdk:
        datahose_loop = bdk.datahose()
        datahose_loop.subscribe(RealTimeEventListenerImpl())
        await datahose_loop.start()


class RealTimeEventListenerImpl(RealTimeEventListener):

    async def on_room_updated(self, initiator: V4Initiator, event: V4RoomUpdated):
        # We do not recommend logging full events in production as it could expose sensitive data
        logging.debug("Room updated: : %s", event.new_room_properties)

    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        # We do not recommend logging full events in production as it could expose sensitive data
        logging.debug("Message sent: %s", event.message.message)

    async def on_room_created(self, initiator: V4Initiator, event: V4RoomCreated):
        # We do not recommend logging full events in production as it could expose sensitive data
        logging.debug("Room created: %s", event.room_properties)

    async def on_instant_message_created(self, initiator: V4Initiator, event: V4InstantMessageCreated):
        logging.debug("IM created: %s", event.stream)

    async def on_message_suppressed(self, initiator: V4Initiator, event: V4MessageSuppressed):
        logging.debug("MSG suppressd: %s", event.message_id)


logging.config.fileConfig(Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False)


try:
    logging.info("Running datahose example...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending datahose example")
