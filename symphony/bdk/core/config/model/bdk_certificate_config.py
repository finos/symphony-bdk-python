class BdkCertificateConfig:
    """Class containing a Certificate configuration
    """

    def __init__(self, path=None, content="", password=None):
        self._path = path
        self._content = content
        self._password = password

    @property
    def path(self):
        """path to certificate file"""
        return self._path

    @property
    def content(self):
        """certificate content string"""
        return self._content

    @property
    def password(self):
        """certificate password string"""
        return self._password

    @content.setter
    def content(self, certificate_content):
        """Sets certificate content and overrides path to None to keep certificate config valid

        :param certificate_content: certificate content
        """
        self._content = certificate_content
        self._path = None

    @path.setter
    def path(self, certificate_path):
        """Sets certificate path and overrides content to None to keep certificate config valid

        :param certificate_path: rsa private key path
        """
        self._path = certificate_path
        self._content = None

    @password.setter
    def password(self, password):
        """Sets certificate password

        :param password: password content
        """
        self._password = password

    def is_configured(self) -> bool:
        """"Check if the certificate authentication is configured or not

        :return: true if the certificate authentication is configured
        """
        return (self._path is not None or self._content != "") and self._password is not None

    def is_valid(self) -> bool:
        """Check if the certificate configuration is valid.
        If both certificate path and content, the configuration is invalid.

        :return: true if the certificate configuration is valid.
        """
        return not (self._path is not None and self._content != "")
