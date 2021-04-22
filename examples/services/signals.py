import asyncio
import logging.config
from pathlib import Path

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.base_signal import BaseSignal


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        signal_service = bdk.signals()

        logging.info('Creating new signal.')
        signal = await signal_service.create_signal(
            BaseSignal(name="Testing signal", query="HASHTAG:hashtag", visible_on_profile=False, company_wide=False))
        logging.info(signal)

        logging.info(await signal_service.get_signal(signal.id))

        logging.info('Add a subscriber to the signal.')
        await signal_service.subscribe_users_to_signal(signal.id, True, [13056700580913])

        logging.info('Unsubscribe added user to the signal.')
        await signal_service.unsubscribe_users_to_signal(signal.id, [13056700580913])

        logging.info("Listing all signals")
        async for s in await signal_service.list_all_signals():
            logging.debug(s)

        logging.info("List all subscribers")
        async for s in await signal_service.list_all_subscribers(signal.id):
            logging.debug(s)

        logging.info(await signal_service.delete_signal(signal.id))


logging.config.fileConfig(Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False)

asyncio.run(run())
