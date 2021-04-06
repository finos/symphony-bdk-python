import asyncio
import logging.config
from pathlib import Path

from symphony.bdk.core.activity.user_joined_room import UserJoinedRoomActivity, UserJoinedRoomContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.symphony_bdk import SymphonyBdk

async def run():
    config = BdkConfigLoader.load_from_symphony_dir("/Users/reed.feldman/devx/test-bot-python/resources/config.yaml")
    async with SymphonyBdk(config) as bdk:
        await bdk.activities().register(JoinRoomActivity(bdk.messages()))
        await bdk.datafeed().start()


class JoinRoomActivity(UserJoinedRoomActivity):
    def __init__(self, messages: MessageService):
        self.messages = messages

    def matches(self, context: UserJoinedRoomContext) -> bool:
        return True

    async def on_activity(self, context: UserJoinedRoomContext):
        await self.messages.send_message(context.source_event.stream.stream_id,
                                         "<messageML>Welcome to the room</messageML>")


logging.config.fileConfig(Path(__file__).parent / "../logging.conf", disable_existing_loggers=False)


try:
    logging.info("Running datafeed example...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending datafeed example")