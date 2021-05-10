import asyncio
import logging.config
import os
from pathlib import Path

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.pod_model.user_filter import UserFilter
from symphony.bdk.gen.pod_model.user_search_filter import UserSearchFilter
from symphony.bdk.gen.pod_model.user_search_query import UserSearchQuery


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        user_service = bdk.users()

        logging.info(await user_service.list_users_by_ids([12987981103610]))

        query = UserSearchQuery(query="bot", filters=UserSearchFilter(company="Symphony"))
        async for uid in await user_service.search_all_users(query, local=False):
            logging.debug(uid)

        async for i in await user_service.list_all_user_details_by_filter(user_filter=UserFilter(status="ENABLED",
                                                                                                 role="INDIVIDUAL"),
                                                                          max_number=100):
            logging.debug(i.user_attributes.display_name)

logging.config.fileConfig(Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False)

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(run())
