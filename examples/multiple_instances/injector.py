"""A bot (named benchmark-injector) sending messages to a room and checking that all messages have been replied to.
"""
import asyncio
import logging.config
from datetime import datetime
from pathlib import Path

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.message.message_parser import get_text_content_from_message
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.pod_model.v3_room_attributes import V3RoomAttributes

# the ID of the bot running reader.py
REPLIER_BOT_ID = 12987981106157

# A real user id so you can visualize the test with the client (user will be added to the test room)
ADMIN_ID = 12987981103693

# Number of messages to test
NUMBER_OF_MESSAGES = 10


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config_injector.yaml")
    async with SymphonyBdk(config) as bdk:
        stream_id = await create_test_room(bdk.streams())

        await send_messages(bdk.messages(), stream_id)
        await check_all_messages_have_been_replied_to(bdk.messages(), config.bot.username, stream_id)


async def create_test_room(streams):
    start_date = datetime.now().isoformat()
    room = await streams.create_room(
        V3RoomAttributes(name=f"Test-{start_date}", description=f"Test-{start_date}", public=True, discoverable=True))
    stream_id = room.room_system_info.id

    await streams.add_member_to_room(REPLIER_BOT_ID, stream_id)
    await streams.add_member_to_room(ADMIN_ID, stream_id)

    logging.debug("Created stream %s", stream_id)
    return stream_id


async def send_messages(messages, stream_id):
    for i in range(NUMBER_OF_MESSAGES):
        await messages.send_message(stream_id, f"<messageML><b>{i}</b> {datetime.now().isoformat()}</messageML>")
    logging.debug("Messages sent")


async def check_all_messages_have_been_replied_to(message_service: MessageService, injector_bot_username, stream_id):
    messages = await message_service.list_messages(stream_id, 0, 0, 2 * NUMBER_OF_MESSAGES)
    while len(messages) != 2 * NUMBER_OF_MESSAGES:
        sent_ids = extract_ids(filter(lambda m: m.user.username == injector_bot_username, messages))
        replied_ids = extract_ids(filter(lambda m: m.user.user_id == REPLIER_BOT_ID, messages))

        logging.debug("Not replied to all messages yet (%s/%s), missing messages: %s", len(messages),
                      2 * NUMBER_OF_MESSAGES, sent_ids - replied_ids)
        await asyncio.sleep(0.1)
        messages = await message_service.list_messages(stream_id, 0, 0, 2 * NUMBER_OF_MESSAGES)
    logging.debug("Replied to all messages")


def extract_ids(iterable):
    return set(map(lambda m: get_text_content_from_message(m).split(" ")[0], iterable))


logging.config.fileConfig(Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False)

if __name__ == "__main__":
    asyncio.run(run())
