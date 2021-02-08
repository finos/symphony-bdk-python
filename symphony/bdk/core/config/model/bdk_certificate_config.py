class BdkCertificateConfig:
    """Class containing a Certificate configuration
    """

    def __init__(self, path=None, content="", password=None):
        self.path = path
        self.content = content
        self.password = password

    def is_configured(self) -> bool:
        """"Check if the certificate authentication is configured or not

        :return: true if the certificate authentication is configured
        """
        return (self.path is not None or self.content != "") and self.password is not None

    def is_valid(self) -> bool:
        """Check if the certificate configuration is valid.
        If both certificate path and content, the configuration is invalid.

        :return: true if the certificate configuration is valid.
        """
        return not (self.path is not None and self.content != "")
