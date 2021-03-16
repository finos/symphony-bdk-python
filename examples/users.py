import asyncio
import logging

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.pod_model.user_filter import UserFilter
from symphony.bdk.gen.pod_model.user_search_filter import UserSearchFilter
from symphony.bdk.gen.pod_model.user_search_query import UserSearchQuery


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

    async with SymphonyBdk(config) as bdk:
        user_service = bdk.users()
        details = await user_service.list_users_by_ids([12987981103610])
        logging.info(details)

        async for uid in await user_service.list_all_users_following(12987981103233):
            print(uid)

        async for i in await user_service.list_all_user_followers(12987981103233):
            print(i)

        query = UserSearchQuery(query='bot', filters=UserSearchFilter(company='Symphony'))
        async for uid in await user_service.search_all_users(query, local=False):
            print(uid)

        async for i in await user_service.list_all_user_details(max_number=100):
            print(i.user_system_info.id)

        async for i in await user_service.list_all_user_details_by_filter(user_filter=UserFilter(status="ENABLED",
                                                                                                 role="INDIVIDUAL"),
                                                                          max_number=100):
            print(i.user_attributes.display_name)


logging.basicConfig(level=logging.DEBUG)
asyncio.run(run())
