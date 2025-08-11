"""A simple bot (named benchmark-reader), reading a datafeed and replying to a message with the same content.
The goal is to run multiple instances of it, hence it adds a unique id and uses a random color in the reply.
"""

import asyncio
import logging.config
import uuid
from pathlib import Path
from random import randrange

import hazelcast
from hazelcast import HazelcastClient

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.datafeed.real_time_event_listener import (
    RealTimeEventListener,
)
from symphony.bdk.core.service.message.message_parser import (
    get_text_content_from_message,
)
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent


class EventListener(RealTimeEventListener):
    def __init__(self, messages: MessageService, hz_client: HazelcastClient):
        self._messages = messages
        self._client = hz_client
        self._id = str(uuid.uuid4())
        self._color = hex(randrange(0xFFFFFF + 1))[
            2:
        ]  # substring to remove leading "0x"

    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        lock = self._client.cp_subsystem.get_lock(
            event.message.stream.stream_id
        ).blocking()
        lock.lock()
        try:
            return await self._reply_to_message(event)
        finally:
            lock.unlock()

    async def _reply_to_message(self, event):
        message = event.message
        text_message = get_text_content_from_message(message)
        message_number = text_message.split(" ")[0]
        logging.debug("Received message number %s", message_number)

        processed_events = self._client.get_map("processed_events").blocking()

        logging.debug("Already processed messages: %s", processed_events.values())
        if processed_events.contains_key(message.message_id):
            logging.debug(
                "Message already processed: " + processed_events.get(message.message_id)
            )
            return

        await self._send_reply_message(message.stream.stream_id, text_message)
        processed_events.put(message.message_id, message_number, 60)

    async def _send_reply_message(self, stream_id, text_message):
        reply_message = f'<messageML><span style="color: #{self._color};">{text_message} <b>{self._id}</b></span></messageML>'
        await self._messages.send_message(stream_id, reply_message)


async def run(hz_client):
    async with SymphonyBdk(
        BdkConfigLoader.load_from_symphony_dir("config_reader.yaml")
    ) as bdk:
        datafeed = bdk.datafeed()
        datafeed.subscribe(EventListener(bdk.messages(), hz_client))
        logging.debug("Starting datafeed")
        await datafeed.start()


logging.config.fileConfig(
    Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False
)

if __name__ == "__main__":
    client = hazelcast.HazelcastClient()
    try:
        asyncio.run(run(client))
    except KeyboardInterrupt:
        logging.debug("Stopping bot")
    finally:
        client.shutdown()
