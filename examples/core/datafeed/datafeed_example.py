import asyncio

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent


class AuthMain:

    @staticmethod
    async def run():

        config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

        async with SymphonyBdk(config) as bdk:
            datafeed_loop = bdk.datafeed()
            datafeed_loop.subscribe(RealTimeEventListenerImpl())
            await datafeed_loop.start()


class RealTimeEventListenerImpl(RealTimeEventListener):

    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        print(event)


if __name__ == "__main__":
    asyncio.run(AuthMain.run())
