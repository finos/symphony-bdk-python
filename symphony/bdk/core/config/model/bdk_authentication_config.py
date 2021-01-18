from symphony.bdk.core.config.model.bdk_rsa_key_config import BdkRsaKeyConfig
from symphony.bdk.core.config.model.bdk_certificate_config import BdkCertificateConfig


class BdkAuthenticationConfig:
    """Class that contains the bot authentication configuration
    """
    def __init__(self, private_key=None, certificate=None):
        self.bdk_rsa_key_config = BdkRsaKeyConfig(**private_key) if private_key is not None else BdkRsaKeyConfig()
        self.bdk_certificate_config = BdkCertificateConfig(**certificate) if certificate is not None else BdkCertificateConfig()

    def is_rsa_authentication_configured(self) -> bool:
        """Check if the RSA authentication is configured

        :return true if the RSA authentication is configured
        """
        return self.bdk_rsa_key_config.is_configured()

    def is_rsa_configuration_valid(self) -> bool:
        """Check of the RSA authentication is valid

        :return: True if the the RSA key valid
        """
        return self.bdk_rsa_key_config.is_valid()

    def is_certificate_authentication_configured(self) -> bool:
        """Check if the certificate authentication is configured

        :return true if the certificate authentication is configured
        """
        return self.bdk_certificate_config.is_configured()

    def is_certificate_configuration_valid(self) -> bool:
        """Check of the certificate authentication is valid

        :return: True if the the certificate key valid
        """
        return self.bdk_certificate_config.is_valid()
