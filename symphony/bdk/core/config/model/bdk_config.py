from symphony.bdk.core.config.model.bdk_app_config import BdkAppConfig
from symphony.bdk.core.config.model.bdk_bot_config import BdkBotConfig
from symphony.bdk.core.config.model.bdk_client_config import BdkClientConfig
from symphony.bdk.core.config.model.bdk_server_config import BdkServerConfig
from symphony.bdk.core.config.model.bdk_ssl_config import BdkSslConfig


class BdkConfig(BdkServerConfig):
    """Class containing the Bdk configuration

    :param **config: dict Configuration parameters
    :return self: BdkConfig instance
    """
    def __init__(self, **config):
        super().__init__(scheme=config.get("scheme"), host=config.get("host"), port=config.get("port"),
                         context=config.get("context"))
        self.agent = BdkClientConfig(self, config.get("agent"))
        self.pod = BdkClientConfig(self, config.get("pod"))
        self.key_manager = BdkClientConfig(self, config.get("keyManager"))
        self.session_auth = BdkClientConfig(self, config.get("sessionAuth"))
        self.bot = BdkBotConfig(config.get("bot"))
        self.ssl = BdkSslConfig(config.get("ssl"))
        self.app = BdkAppConfig(config.get("app"))
