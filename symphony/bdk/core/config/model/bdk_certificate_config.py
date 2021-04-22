class BdkCertificateConfig:
    """Class containing a Certificate configuration for certificate authentication.
    For the format of the certificate file to pass, see
    `ssl.SSLContext.load_cert_chain <https://docs.python.org/3/library/ssl.html#ssl.SSLContext.load_cert_chain>`_.
    For now we only fill the ``certfile`` param, so the ``path`` field should contain the certificate and
    the decrypted private key in PEM format.
    """

    def __init__(self, path: str = None):
        """

        :param path: the path to the client certificate file in PEM format
        """
        self._path = path

    @property
    def path(self) -> str:
        """Path to the client certificate file in PEM format.

        :return: the path to the client certificate file
        """
        return self._path

    @path.setter
    def path(self, certificate_path: str):
        """Sets certificate path.

        :param certificate_path: path to a client certificate in PEM format
        """
        self._path = certificate_path

    def is_valid(self) -> bool:
        """Check if the certificate configuration is valid.

        :return: true if the path to the client certificate is not empty
        """
        return self._path is not None and self._path != ""
