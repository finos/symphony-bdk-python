import asyncio
import logging

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.base_signal import BaseSignal


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        signal_service = bdk.signals()
        attribute_map = {
            'name': 'Testing signal',
            'query': 'HASHTAG:hashtag',
            'visible_on_profile': False,
            'company_wide': False
        }
        logging.info('Creating new signal.')
        signal = await signal_service.create_signal(BaseSignal(**attribute_map))
        logging.info(signal)
        await signal_service.list_signals(0, 3)
        attribute_map_update = {
            'name': 'Testing signal updated',
            'query': 'HASHTAG:hashtag',
            'visible_on_profile': False,
            'company_wide': False
        }
        logging.info('Updating signal.')
        await signal_service.update_signal(signal.id, BaseSignal(**attribute_map_update))
        logging.info(await signal_service.get_signal(signal.id))
        logging.info('Add a subscriber to the signal.')
        await signal_service.subscribe_users_to_signal(signal.id, True, [13056700580913])
        logging.info(await signal_service.list_subscribers(signal.id))
        logging.info('Unsubscribe added user to the signal.')
        await signal_service.unsubscribe_users_to_signal(signal.id, [13056700580913])
        logging.info(await signal_service.list_subscribers(signal.id))
        logging.info(await signal_service.delete_signal(signal.id))

        logging.info("Listing all signals")
        async for s in await signal_service.list_all_signals():
            print(s)

        logging.info("List all subscribers")
        async for s in await signal_service.list_all_subscribers(signal.id):
            print(s)


logging.basicConfig(level=logging.DEBUG)
asyncio.run(run())
