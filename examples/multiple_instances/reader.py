import asyncio
import logging.config
import uuid
from pathlib import Path
from random import randrange

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.service.message.message_parser import get_text_content_from_message
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent


class EventListener(RealTimeEventListener):

    def __init__(self, messages: MessageService):
        self._messages = messages
        self._id = str(uuid.uuid4())
        self._color = hex(randrange(0xffffff + 1))[2:]  # substring to remove leading "0x"

    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        logging.debug("received message")
        text_message = get_text_content_from_message(event.message)
        reply_message = f"<messageML><span style=\"color: #{self._color};\">{text_message} <b>{self._id}</b></span></messageML>"
        await self._messages.send_message(event.message.stream.stream_id, reply_message)


async def reply_to_messages():
    async with SymphonyBdk(BdkConfigLoader.load_from_symphony_dir("config_bot_elias.yaml")) as bdk:
        datafeed = bdk.datafeed()
        datafeed.subscribe(EventListener(bdk.messages()))
        logging.debug("starting datafeed")
        await datafeed.start()


logging.config.fileConfig(Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False)

if __name__ == "__main__":
    asyncio.run(reply_to_messages())
