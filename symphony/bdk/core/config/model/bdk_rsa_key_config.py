class BdkRsaKeyConfig:
    """Class containing the bot's RSA Key configuration
    """
    def __init__(self, path=None, content=""):
        self._path = path
        self._content = content

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

    def set_content(self, rsa_key_content):
        """Sets rsa content and overrides path to None to keep key's config valid

        :param rsa_key_content: rsa private key content
        """
        self._content = rsa_key_content
        self._path = None

    def set_path(self, rsa_key_path):
        """Sets rsa path and overrides content to None to keep key's config valid
        :param rsa_key_path: rsa private key path
        """
        self._path = rsa_key_path
        self._content = None

    def get_private_key_from_config(self):
        """Loads the private key content.
        If the path is set, it loads the file content, otherwise it returns the content.

        :return: private key content as string.
        """
        return self._load_key_from_path() \
            if self._path is not None else self._content

    def _load_key_from_path(self):
        if self._path is not None:
            with open(self._path, "r") as f:
                private_key_content = f.readlines()
                key = "".join(private_key_content)
                return key
        return ""

    path = property(fset=set_path, doc="path to rsa private key file")
    content = property(fset=set_content, doc="rsa private key content as a string")