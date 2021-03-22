class BdkRsaKeyConfig:
    """Class containing the bot's RSA Key configuration
    """
    def __init__(self, path=None, content=""):
        self._path = path
        self._content = content

    @property
    def path(self):
        """Path to rsa private key file."""
        return self._path

    @property
    def content(self):
        """rsa private key content string"""
        return self._content

    @content.setter
    def content(self, rsa_key_content):
        """Sets rsa content and overrides path to None to keep key's config valid

        :param rsa_key_content: rsa private key content
        """
        self._content = rsa_key_content
        self._path = None

    @path.setter
    def path(self, rsa_key_path):
        """Sets rsa path and overrides content to None to keep key's config valid
        :param rsa_key_path: rsa private key path
        """
        self._path = rsa_key_path
        self._content = None

    def is_configured(self) -> bool:
        """"Check if the RSA authentication is configured or not

        :return: true if the RSA authentication is configured
        """
        return self._path is not None or self._content != ""

    def is_valid(self) -> bool:
        """Check if the RSA configuration is valid.
        If both of private key path and content, the configuration is invalid.

        :return: true if the RSA configuration is valid.
        """
        return not (self._path is not None and self._content != "")

    def get_private_key_content(self) -> str:
        """Loads the private key content.
        If the path is set, it loads the file content, otherwise it returns the content.

        :return: private key content as string.
        """
        return self._load_key_from_path() \
            if self._path is not None else self._content

    def _load_key_from_path(self):
        with open(self._path, "r") as file:
            private_key_content = file.readlines()
            key = "".join(private_key_content)
            return key
