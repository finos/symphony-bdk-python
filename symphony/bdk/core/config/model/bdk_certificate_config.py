class BdkCertificateConfig:
    """Class containing a Certificate configuration
    """
    def __init__(self, path=None, content="", password=None, **kwargs):
        self._path = path
        self._content = content
        self._password = password

    def is_configured(self) -> bool:
        """"Check if the certificate authentication is configured or not

        :return: true if the certificate authentication is configured
        """
        return self.path is not None or self.content

    def is_valid(self) -> bool:
        """Check if the certificate configuration is valid.
        If both certificate path and content, the configuration is invalid.

        :return: true if the RSA configuration is invalid.
        """
        return self.path is not None and self.content

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

