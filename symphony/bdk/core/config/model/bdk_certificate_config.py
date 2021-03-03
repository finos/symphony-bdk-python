class BdkCertificateConfig:
    """Class containing a Certificate configuration
    """

    def __init__(self, path=None, content="", password=None):
        self._path = path
        self._content = content
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

    def set_content(self, certificate_content):
        """Sets ceritficate content and overrides path to None to keep certificate config valid

        :param certificate_content: certificate content
        """
        self._content = certificate_content
        self._path = None

    def set_path(self, certificate_path):
        """Sets certificate path and overrides content to None to keep certificate config valid

        :param certificate_path: rsa private key path
        """
        self._path = certificate_path
        self._content = None

    def set_password(self, password):
        """Sets certificate password

        :param password: password content
        """
        self._password = password

    path = property(fset=set_path, doc="path to certificate file")
    content = property(fset=set_content, doc="certificate content as a string")
    password = property(fset=set_password, doc="certificate password as a string")

