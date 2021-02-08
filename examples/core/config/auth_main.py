import asyncio

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


class AuthMain:

    @staticmethod
    async def run():

        config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
        async with SymphonyBdk(config) as bdk:
            auth_session = bdk.bot_session()
            print(await auth_session.key_manager_token)
            print(await auth_session.session_token)
            print("Obo example:")
            obo_auth_session = bdk.obo(username="username")
            print(await obo_auth_session.session_token)


if __name__ == "__main__":
    asyncio.run(AuthMain.run())
