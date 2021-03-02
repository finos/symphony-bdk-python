class BdkRsaKeyConfig:
    """Class containing the bot's RSA Key configuration
    """
    def __init__(self, path=None, content=""):
        self.path = path
        self.content = content

    def is_configured(self) -> bool:
        """"Check if the RSA authentication is configured or not

        :return: true if the RSA authentication is configured
        """
        return self.path is not None or self.content != ""

    def is_valid(self) -> bool:
        """Check if the RSA configuration is valid.
        If both of private key path and content, the configuration is invalid.

        :return: true if the RSA configuration is valid.
        """
        return not (self.path is not None and self.content != "")

    def setContent(self, rsa_key_content):
        """Sets rsa content and overrides path to None to keep key's config valid
        Args:
            rsa_content: rsa private key content
        """
        self.content = rsa_key_content
        self.path = None

    def setPath(self, rsa_key_path):
        """Sets rsa path and overrides content to None to keep key's config valid
        Args:
            rsa_path: rsa private key path
        """
        self.path = rsa_key_path
        self.content = None
