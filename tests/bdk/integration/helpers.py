import asyncio
import os
import re

import pytest
import pytest_asyncio
import yaml
from pathlib import Path

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.datafeed.real_time_event_listener import \
    RealTimeEventListener
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent

STREAM_ID = os.getenv("STREAM_ID")
MSG_BOT_USERNAME = os.getenv("MSG_BOT_USERNAME")
FEED_BOT_USERNAME = os.getenv("FEED_BOT_USERNAME")
SYMPHONY_HOST = os.getenv("SYMPHONY_HOST")
TEST_RSA_KEY = os.getenv("TEST_RSA_KEY")
TEST_USER_ID = os.getenv("TEST_USER_ID")
BOT_USER_ID = os.getenv("BOT_USER_ID")
NUMBER_OF_MESSAGES = 3


def generate_config(tmp_dir: Path, bot_username: str):
    key_path = tmp_dir / "key.pem"
    config_path = tmp_dir / "config.yaml"

    bot_config_dict = {
        "host": SYMPHONY_HOST,
        "bot": {"username": bot_username, "privateKey": {"path": str(key_path)}},
    }

    key_path.write_text(TEST_RSA_KEY)
    with config_path.open("w") as config_file:
        yaml.dump(bot_config_dict, config_file)

    return config_path


@pytest.fixture
def messenger_bot_config(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("bdk_config_messenger")
    return generate_config(tmp_dir, MSG_BOT_USERNAME)


@pytest.fixture
def datafeed_bot_config(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("bdk_config_feed")
    return generate_config(tmp_dir, FEED_BOT_USERNAME)


@pytest_asyncio.fixture
async def bdk(messenger_bot_config):
    config = BdkConfigLoader.load_from_file(str(messenger_bot_config))
    async with SymphonyBdk(config) as bdk:
        yield bdk


async def send_messages(messages, stream_id, since, uuid):
    for i in range(NUMBER_OF_MESSAGES):
        await messages.send_message(
            stream_id, f"<messageML><b>{uuid}-{i}-{since}</b></messageML>"
        )


async def get_test_messages(bdk, since, uuid):
    messages = await bdk.messages().list_messages(STREAM_ID, since=since)
    cleaned_messages_text = [
        re.sub(r"<[^>]+>", " ", msg["message"]).strip() for msg in messages
    ]
    return list(
        filter(
            lambda msg: msg.startswith(uuid),
            cleaned_messages_text,
        )
    )


class MessageListener(RealTimeEventListener):
    """A simple listener to capture a specific message from the datafeed."""

    def __init__(self, message_to_find: str):
        self._message_to_find = message_to_find
        self.message_received_event = asyncio.Event()

    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        message_text = re.sub(r"<[^>]+>", "", event.message.message).strip()
        if self._message_to_find in message_text:
            self.message_received_event.set()
