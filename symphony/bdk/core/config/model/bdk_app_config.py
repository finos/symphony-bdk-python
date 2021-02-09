from symphony.bdk.core.config.model.bdk_authentication_config import BdkAuthenticationConfig


class BdkAppConfig(BdkAuthenticationConfig):
    """Class containing the extension app configuration
    """

    def __init__(self, config):
        if config is not None:
            self.app_id = config.get("appId")
            super().__init__(private_key_config=config.get("privateKey"), certificate_config=config.get("certificate"))
        else:
            super().__init__()
