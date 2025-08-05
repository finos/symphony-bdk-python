import os
import yaml
from pytest import fixture, mark
import re
from datetime import datetime, timedelta

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk



NUMBER_OF_MESSAGES = 10
STREAM_ID = os.getenv("STREAM_ID", "put-stream-id-to-env-vars")
CONFIG_PATH = "./config.yaml"

@fixture
def bot_config():
    bot_user = os.getenv("BOT_USERNAME", "put-useranme-to-env-vars")
    sym_host = os.getenv("SYMPHONY_HOST", "put-symphony-host-to-env-vars")
    key_path = "./key.pem"
    bot_config = {"host": sym_host,
                  "bot": {"username": bot_user, "privateKey": {"path": key_path}}}
    with open(CONFIG_PATH, "w") as config_file:
        yaml.dump(bot_config, config_file)

    with open(key_path, "w") as key_file:
        key_file.write(os.getenv("TEST_RSA_KEY", "PUT A KEY HERE OR INTO ENV VAR"))
    yield
    os.remove(key_path), os.remove(CONFIG_PATH)

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


@mark.asyncio
async def test_bot_read_write_messages(bot_config):
    # Given: test execution start time
    since = int((datetime.now() - timedelta(seconds=2)).timestamp()) * 1000
    # Given: BDK is initialized with config
    config = BdkConfigLoader.load_from_symphony_dir(CONFIG_PATH)
    async with SymphonyBdk(config) as bdk:
        # When: messages are sent via bot
        await send_messages(bdk.messages(), STREAM_ID, since)
        # Then: messages are readable with the same bot
        messages = await get_test_messages(bdk, since)
    # Then: Expected messages are posted to the room
    assert sorted(messages) == [f"{i}-{since}" for i in range(NUMBER_OF_MESSAGES)]