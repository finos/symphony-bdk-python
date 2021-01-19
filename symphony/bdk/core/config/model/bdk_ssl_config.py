from symphony.bdk.core.config.model.bdk_certificate_config import BdkCertificateConfig


class BdkSslConfig:
    """Class containing the ssl configuration
    """

    def __init__(self, config):
        if config is not None and "trustStore" in config:
            truststore_config = config.get("trustStore")
            self.trust_store = BdkCertificateConfig(path=truststore_config.get("path"),
                                                    password=truststore_config.get("password"))
        else:
            self.trust_store = BdkCertificateConfig()