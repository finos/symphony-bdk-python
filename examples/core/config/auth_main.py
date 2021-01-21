import asyncio
from symphony.bdk.core.config.bdk_config_loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


class AuthMain:

    @staticmethod
    async def run():

        config_3 = BdkConfigLoader.load_from_symphony_dir("config.yaml")
        bdk = SymphonyBdk(config_3)
        auth_session = await bdk.bot_session()
        print(auth_session.key_manager_token)
        print(auth_session.session_token)


if __name__ == "__main__":
    asyncio.run(AuthMain.run())
