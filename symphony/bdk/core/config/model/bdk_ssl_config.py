from symphony.bdk.core.config.model.bdk_certificate_config import BdkCertificateConfig

TRUST_STORE = "trustStore"


class BdkSslConfig:
    """Class containing the SSL configuration.
    """

    def __init__(self, config):
        """

        :param config: the dict containing the SSL specific configuration.
        """
        if config is not None and TRUST_STORE in config:
            truststore_config = config.get(TRUST_STORE)
            self.trust_store = BdkCertificateConfig(path=truststore_config.get("path"),
                                                    password=truststore_config.get("password"))
        else:
            self.trust_store = BdkCertificateConfig()
