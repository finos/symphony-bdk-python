from symphony.bdk.core.config.model.bdk_authentication_config import BdkAuthenticationConfig


class BdkBotConfig(BdkAuthenticationConfig):
    """Class containing the bot configuration
    """
    def __init__(self, config):
        if config is not None:
            self._username = config.get("username")
            super().__init__(private_key=config.get("privateKey"), certificate=config.get("certificate"))
        else:
            super().__init__()

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value


