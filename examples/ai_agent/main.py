import asyncio
import logging.config
from pathlib import Path

from examples.ai_agent.agent import build_agent
from examples.ai_agent.ask_ai_activity import AskAiActivity
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    async with SymphonyBdk(BdkConfigLoader.load_from_symphony_dir("config.yaml")) as bdk:
        agent = build_agent(bdk)
        bdk.activities().register(AskAiActivity(bdk.messages(), agent))
        await bdk.datafeed().start()


logging.config.fileConfig(
    Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False
)

try:
    logging.info("Running AI agent example...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending AI agent example")
