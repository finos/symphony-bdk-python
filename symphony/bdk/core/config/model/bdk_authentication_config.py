"""Module handling authentication part of the configuration.
"""
from symphony.bdk.core.config.model.bdk_rsa_key_config import BdkRsaKeyConfig
from symphony.bdk.core.config.model.bdk_certificate_config import BdkCertificateConfig


class BdkAuthenticationConfig:
    """Class that contains the bot authentication configuration:
    - either private key configuration for RSA authentication
    - or certificate configuration for certificate authentication.
    """

    def __init__(self, private_key_config=None, certificate_config=None):
        self.private_key = BdkRsaKeyConfig(
            **private_key_config) if private_key_config is not None else BdkRsaKeyConfig()
        self.certificate = BdkCertificateConfig(
            **certificate_config) if certificate_config is not None else BdkCertificateConfig()

    def is_authentication_configured(self) -> bool:
        """Check if either RSA or certificate authentication is configured

        :return: True if RSA or certificate authentication is configured
        """
        return self.is_rsa_configuration_valid() or self.is_certificate_configuration_valid()

    def is_rsa_authentication_configured(self) -> bool:
        """Check if the RSA authentication is configured

        :return True if the RSA authentication is configured
        """
        return self.private_key.is_configured()

    def is_rsa_configuration_valid(self) -> bool:
        """Check of the RSA authentication is valid

        If both of private_key path and content, the configuration is invalid.
        :return: True if the the RSA key valid
        """
        return self.private_key.is_configured() and self.private_key.is_valid()

    def is_certificate_configuration_valid(self) -> bool:
        """Check of the certificate authentication is valid

        If both of certificate key path and content, the configuration is invalid.
        :return: True if the the certificate key valid
        """
        return self.certificate.is_valid()
