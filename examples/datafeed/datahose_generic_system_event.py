import asyncio
import logging
import logging.config
from pathlib import Path

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.v4_generic_system_event import V4GenericSystemEvent
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator

# Required config.yaml datahose section:
#
# datahose:
#   tag: my-bot-tag
#   eventTypes:
#     - GENERICSYSTEMEVENT


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        datahose_loop = bdk.datahose()
        datahose_loop.subscribe(RealTimeEventListenerImpl())
        await datahose_loop.start()


class RealTimeEventListenerImpl(RealTimeEventListener):
    async def on_generic_system_event(self, initiator: V4Initiator, event: V4GenericSystemEvent):
        """Called for every GENERICSYSTEMEVENT received from the datahose.

        GENERICSYSTEMEVENT is a platform-level envelope emitted by Symphony's internal
        Maestro event bus. The ``event_subtype`` field identifies the specific event;
        ``parameters`` carries subtype-specific data whose structure varies per subtype.

        Always filter on ``event_subtype`` — do not act on every generic event blindly.
        """
        subtype = event.event_subtype

        # We do not recommend logging full events in production as it could expose sensitive data
        logging.debug("GenericSystemEvent received — subtype: %s", subtype)

        # Filter on the specific subtype relevant to your use case.
        # The subtype values are defined by your Symphony deployment; log them first
        # to discover which ones are relevant before adding conditional logic.
        if subtype == "CONNECTION_REQUEST_ALERT":
            # Example: a federation connection lifecycle event.
            # event.parameters contains subtype-specific fields.
            logging.info("Connection request alert — parameters: %s", event.parameters)

        elif subtype is None:
            logging.warning("Received GENERICSYSTEMEVENT with no event_subtype — skipping")

        else:
            logging.debug("Unhandled GENERICSYSTEMEVENT subtype: %s", subtype)


logging.config.fileConfig(
    Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False
)


try:
    logging.info("Running datahose generic system event example...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending datahose generic system event example")
