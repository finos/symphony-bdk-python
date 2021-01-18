from symphony.bdk.core.config.model.bdk_certificate_config import BdkCertificateConfig


class BdkSslConfig:
    """Class containing the ssl configuration
    """
    def __init__(self, config):
        if config is not None:
            self._trust_store = BdkCertificateConfig(
                **config.get("trustStore")) if "trustStore" in config else BdkCertificateConfig()
        else:
            self._trust_store = BdkCertificateConfig()

    @property
    def trusts_store(self):
        return self._trust_store

    @trusts_store.setter
    def trusts_store(self, value):
        self._trust_store = value
