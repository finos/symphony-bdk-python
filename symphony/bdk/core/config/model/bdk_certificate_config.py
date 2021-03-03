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

    def set_content(self, certificate_content):
        """Sets ceritficate content and overrides path to None to keep certificate config valid
        Args:
            certificate_content: certificate content
        """
        self.content = certificate_content
        self.path = None

    def set_path(self, certificate_path):
        """Sets certificate path and overrides content to None to keep certificate config valid
        Args:
            certificate_path: rsa private key path
        """
        self.path = certificate_path
        self.content = None

