from symphony.bdk.core.config.model.bdk_authentication_config import BdkAuthenticationConfig


class BdkBotConfig(BdkAuthenticationConfig):

    def __init__(self, config):
        if config is not None:
            self.__username = config.get("username")
            super().__init__(private_key=config.get("privateKey"), certificate=config.get("certificate"))
        else:
            super().__init__()

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, value):
        self.__username = value


