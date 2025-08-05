import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import yaml

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk

STREAM_ID = os.getenv("STREAM_ID")
BOT_USERNAME = os.getenv("BOT_USERNAME")
SYMPHONY_HOST = os.getenv("SYMPHONY_HOST")
TEST_RSA_KEY = os.getenv("TEST_RSA_KEY")

# Skip all tests in this file if the required environment variables are not set.
pytestmark = pytest.mark.skipif(
    not all([STREAM_ID, BOT_USERNAME, SYMPHONY_HOST, TEST_RSA_KEY]),
    reason="Required environment variables for integration tests are not set "
           "(STREAM_ID, BOT_USERNAME, SYMPHONY_HOST, TEST_RSA_KEY)"
)

NUMBER_OF_MESSAGES = 10
@pytest.fixture
def bot_config_path(tmp_path: Path):
    key_path = tmp_path / "key.pem"
    config_path = tmp_path / "config.yaml"


    bot_config_dict = {
        "host": SYMPHONY_HOST,
        "bot": {
            "username": BOT_USERNAME,
            "privateKey": {"path": str(key_path)}
        }
    }

    # Write the key and config files
    key_path.write_text(TEST_RSA_KEY)
    with config_path.open("w") as config_file:
        yaml.dump(bot_config_dict, config_file)

    yield config_path

    os.remove(key_path), os.remove(config_path)

async def send_messages(messages, stream_id, since):
    for i in range(NUMBER_OF_MESSAGES):
        await messages.send_message(stream_id, f"<messageML><b>{i}-{since}</b></messageML>")

async def get_test_messages(bdk, since):
    messages = await bdk.messages().list_messages(STREAM_ID, since=since)
    cleaned_messages_text = [
      re.sub(r"<[^>]+>", " ", msg["message"]).strip()
        for msg in messages
    ]
    return cleaned_messages_text


@pytest.mark.asyncio
async def test_bot_read_write_messages(bot_config_path):
    # Given: test execution start time
    since = int((datetime.now() - timedelta(seconds=2)).timestamp()) * 1000
    # Given: BDK is initialized with config
    config = BdkConfigLoader.load_from_symphony_dir(str(bot_config_path))
    async with SymphonyBdk(config) as bdk:
        # When: messages are sent via bot
        await send_messages(bdk.messages(), STREAM_ID, since)
        # Then: messages are readable with the same bot
        messages = await get_test_messages(bdk, since)
    # Then: Expected messages are posted to the room
    assert sorted(messages) == [f"{i}-{since}" for i in range(NUMBER_OF_MESSAGES)]