import asyncio

from symphony.bdk.core.config.bdk_config_loader import BdkConfigLoader
from symphony.bdk.core.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent


class AuthMain:

    @staticmethod
    async def run():

        config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
        bdk = SymphonyBdk(config)
        try:
            auth_session = await bdk.bot_session()
            print("authentication successful", auth_session.session_token, auth_session.key_manager_token, sep="\n")
            bdk.datafeed().subscribe(RealTimeEventListenerImpl())
            await bdk.datafeed().start()
        finally:
            await bdk.close_clients()


class RealTimeEventListenerImpl(RealTimeEventListener):

    def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        print(event)


if __name__ == "__main__":
    asyncio.run(AuthMain.run())
