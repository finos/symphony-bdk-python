from symphony.bdk.core.config.model.bdk_certificate_config import BdkCertificateConfig


class BdkSslConfig:
    """Class containing the ssl configuration
    """
    def __init__(self, config):
        if config is not None:
            self.trust_store = BdkCertificateConfig(
                **config.get("trustStore")) if "trustStore" in config else BdkCertificateConfig()
        else:
            self.trust_store = BdkCertificateConfig()