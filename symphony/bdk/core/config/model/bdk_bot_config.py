from symphony.bdk.core.config.model.bdk_authentication_config import BdkAuthenticationConfig


class BdkBotConfig(BdkAuthenticationConfig):
    """Class containing the bot configuration
    """
    def __init__(self, config):
        if config is not None:
            self.username = config.get("username")
            super().__init__(private_key=config.get("privateKey"), certificate=config.get("certificate"))
        else:
            super().__init__()
