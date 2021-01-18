from symphony.bdk.core.config.model.bdk_bot_config import BdkBotConfig
from symphony.bdk.core.config.model.bdk_server_config import BdkServerConfig
from symphony.bdk.core.config.model.bdk_client_config import BdkClientConfig
from symphony.bdk.core.config.model.bdk_ssl_config import BdkSslConfig


class BdkConfig(BdkServerConfig):
    """Class containing the Bdk configuration

    :param **config: dict Configuration parameters
    :return self: BdkConfig instance
    """
    def __init__(self, **config):
        super().__init__(scheme=config.get("scheme"), host=config.get("host"), port=config.get("port"),
                         context=config.get("context"))
        self.__agent = BdkClientConfig(self, config.get("agent"))
        self.__pod = BdkClientConfig(self, config.get("pod"))
        self.__key_manager = BdkClientConfig(self, config.get("keyManager"))
        self.__session_auth = BdkClientConfig(self, config.get("sessionAuth"))

        self.__bot = BdkBotConfig(config.get("bot"))
        self.__ssl = BdkSslConfig(config.get("ssl"))

    @property
    def agent(self): return self.__agent

    @agent.setter
    def agent(self, value): self.__agent = value

    @property
    def pod(self): return self.__pod

    @pod.setter
    def pod(self, value): self.__pod = value

    @property
    def key_manager(self): return self.__key_manager

    @key_manager.setter
    def key_manager(self, value): self.__key_manager = value

    @property
    def session_auth(self): return self.__session_auth

    @session_auth.setter
    def session_auth(self, value): self.__session_auth = value

    @property
    def bot(self): return self.__bot

    @bot.setter
    def bot(self, value): self.__bot = value

    @property
    def ssl(self): return self.__ssl

    @ssl.setter
    def ssl(self, value): self.__ssl = value
