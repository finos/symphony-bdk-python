import asyncio
import logging.config
import time
from pathlib import Path

from symphony.bdk.core.activity.command import CommandContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.v4_message import V4Message


async def run():
    async with SymphonyBdk(
        BdkConfigLoader.load_from_symphony_dir("config.yaml")
    ) as bdk:
        activities = bdk.activities()
        messages = bdk.messages()

        @activities.slash("/go")
        async def on_hello(context: CommandContext):
            pick_emoji = [
                "cat",
                "dromedary_camel",
                "dolphin",
                "dog",
                "hamster",
                "goat",
                "panda_face",
                "koala",
                "frog",
                "penguin",
            ]

            previous_message: V4Message = await messages.send_message(
                context.stream_id, "Let the show begin!"
            )

            for i in range(0, len(pick_emoji)):
                time.sleep(1)
                mml = '<emoji shortcode="{}" /><br/><br/>Update <b>#{}</b>'.format(
                    pick_emoji[i], (i + 1)
                )
                previous_message = await messages.update_message(
                    previous_message.stream.stream_id, previous_message.message_id, mml
                )

        await bdk.datafeed().start()


logging.config.fileConfig(
    Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False
)

asyncio.run(run())
