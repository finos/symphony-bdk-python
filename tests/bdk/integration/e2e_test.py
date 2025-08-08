import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.pod_model.v3_room_attributes import V3RoomAttributes
from tests.bdk.integration.helpers import (BOT_USER_ID, FEED_BOT_USERNAME,
                                           MSG_BOT_USERNAME, STREAM_ID,
                                           SYMPHONY_HOST, TEST_RSA_KEY,
                                           TEST_USER_ID, MessageListener,
                                           datafeed_bot_config,
                                           get_test_messages,
                                           messenger_bot_config, send_messages)

pytestmark =[
    pytest.mark.asyncio,
 pytest.mark.skipif(
    not all(
        [
            STREAM_ID,
            MSG_BOT_USERNAME,
            FEED_BOT_USERNAME,
            SYMPHONY_HOST,
            TEST_RSA_KEY,
            TEST_USER_ID,
            BOT_USER_ID,
        ]
    ),
    reason="Required environment variables for integration tests are not set "
    "(STREAM_ID, MSG_BOT_USERNAME, FEED_BOT_USERNAME, SYMPHONY_HOST, TEST_RSA_KEY, TEST_USER_ID, BOT_USER_ID)",
)
]
NUMBER_OF_MESSAGES = 3


@pytest_asyncio.fixture
async def bdk(messenger_bot_config):
    config = BdkConfigLoader.load_from_file(str(messenger_bot_config))
    async with SymphonyBdk(config) as bdk:
        yield bdk


@pytest.mark.asyncio
async def test_bot_read_write_messages(bdk):
    uuid = str(uuid4())
    # Given: test execution start time
    since = int((datetime.now() - timedelta(seconds=2)).timestamp()) * 1000
    # Given: BDK is initialized with config
    # When: messages are sent via bot
    await send_messages(bdk.messages(), STREAM_ID, since, uuid)
    # Then: messages are readable with the same bot
    messages = await get_test_messages(bdk, since, uuid)
    # Then: Expected messages are posted to the room
    assert sorted(messages) == [
        f"{uuid}-{i}-{since}" for i in range(NUMBER_OF_MESSAGES)
    ]


@pytest.mark.asyncio
async def test_bot_creates_stream_add_delete_user(bdk):
    test_user = int(TEST_USER_ID)
    # Given: Stream bdk creates a room
    streams = bdk.streams()
    room_result = await streams.create_room(
        V3RoomAttributes(name="New fancy room", description="test room")
    )
    room_id = room_result.room_system_info.id
    # When: user is added to the room
    await streams.add_member_to_room(test_user, room_id)
    members = await streams.list_room_members(room_id)
    # Then: user is present in the room
    assert test_user in [m.id for m in members.value]
    # When: user is removed from the room
    await streams.remove_member_from_room(test_user, room_id)
    # Then: user is deleted from the room
    members_after_removal = await streams.list_room_members(room_id)
    assert test_user not in [m.id for m in members_after_removal.value]


@pytest.mark.asyncio
async def test_datafeed_receives_message(bdk: SymphonyBdk, datafeed_bot_config):
    """
    Test is running 2 bdk instances at the same time.
    Data feed filters its own events so in order to see that feed is working
    Two parale bots are added

    """
    # Given: message listener is initialized with expected message id
    unique_id = str(uuid4())
    message_content = f"Message for datafeed test. ID: {unique_id}"
    listener = MessageListener(message_to_find=message_content)
    # Given: members are added to the room
    bdk.datafeed().subscribe(listener)
    await bdk.streams().add_member_to_room(int(BOT_USER_ID), STREAM_ID)
    datafeed_task = asyncio.create_task(bdk.datafeed().start())
    await asyncio.sleep(3)
    config = BdkConfigLoader.load_from_file(str(datafeed_bot_config))
    async with SymphonyBdk(config) as another_bot:
        # When: another bot instance sends a message to the needed room
        await another_bot.messages().send_message(STREAM_ID, message_content)
    try:
        # Then: particular message is received by datafeed instance
        await asyncio.wait_for(listener.message_received_event.wait(), timeout=300)
    except asyncio.TimeoutError:
        pytest.fail("Datafeed did not receive the message within the timeout period.")
    finally:
        await bdk.datafeed().stop()
        await datafeed_task
        bdk.datafeed().unsubscribe(listener)

    assert listener.message_received_event.is_set()
