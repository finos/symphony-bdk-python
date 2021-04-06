from symphony.bdk.core.config.model.bdk_app_config import BdkAppConfig
from symphony.bdk.core.config.model.bdk_bot_config import BdkBotConfig
from symphony.bdk.core.config.model.bdk_client_config import BdkClientConfig
from symphony.bdk.core.config.model.bdk_server_config import BdkServerConfig
from symphony.bdk.core.config.model.bdk_ssl_config import BdkSslConfig
from symphony.bdk.core.config.model.bdk_datafeed_config import BdkDatafeedConfig


class BdkConfig(BdkServerConfig):
    """Class containing the whole BDK configuration.
    """

    def __init__(self, **config):
        """

        :param config: the dict containing the server configuration parameters.
        """
        super().__init__(scheme=config.get("scheme"), host=config.get("host"), port=config.get("port"),
                         context=config.get("context"), proxy=config.get("proxy"),
                         default_headers=config.get("defaultHeaders"))
        self.agent = BdkClientConfig(self, config.get("agent"))
        self.pod = BdkClientConfig(self, config.get("pod"))
        self.key_manager = BdkClientConfig(self, config.get("keyManager"))
        self.session_auth = BdkClientConfig(self, config.get("sessionAuth"))
        self.bot = BdkBotConfig(config.get("bot"))
        self.ssl = BdkSslConfig(config.get("ssl"))
        self.app = BdkAppConfig(config.get("app"))
        self.datafeed = BdkDatafeedConfig(config.get("datafeed"))

    def is_bot_configured(self) -> bool:
        """

        :return: true if bot service account is specified in the configuration.
        """
        return self.bot.username is not None
