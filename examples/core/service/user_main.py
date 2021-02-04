import asyncio

from symphony.bdk.core.config.bdk_config_loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


class UserMain:

    @staticmethod
    async def run():

        config_3 = BdkConfigLoader.load_from_symphony_dir("config.yaml")

        async with SymphonyBdk(config_3) as bdk:
            user_service = bdk.users()
            details = await user_service.list_users_by_ids([12987981103610])
            print(details)


if __name__ == "__main__":
    asyncio.run(UserMain.run())
