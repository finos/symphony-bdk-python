TRUST_STORE = "trustStore"


class BdkSslConfig:
    """Class containing the SSL configuration.
    self.trust_store_path should be the path to a file of concatenated CA certificates in PEM format."""

    def __init__(self, config):
        """

        :param config: the dict containing the SSL specific configuration.
        """
        self.trust_store_path = None
        if config is not None and TRUST_STORE in config:
            self.trust_store_path = config[TRUST_STORE].get("path")
