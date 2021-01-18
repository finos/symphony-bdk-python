from symphony.bdk.core.config.model.bdk_rsa_key_config import BdkRsaKeyConfig
from symphony.bdk.core.config.model.bdk_certificate_config import BdkCertificateConfig


class BdkAuthenticationConfig:

    def __init__(self, private_key=None, certificate=None):
        self._bdk_rsa_key_config = BdkRsaKeyConfig(**private_key) if private_key is not None else BdkRsaKeyConfig()
        self._bdk_certificate_config = BdkCertificateConfig(**certificate) if certificate is not None else BdkCertificateConfig()

    def is_rsa_authentication_configured(self) -> bool:
        """Check if the RSA authentication is configured

        :return true if the RSA authentication is configured
        """
        return (self.bot_rsa_key_config is not None and self.bot_rsa_key_config.is_configured())

    def is_rsa_configuration_valid(self) -> bool:
        """Check of the RSA authentication is valid

        :return: True if the the RSA key valid
        """
        return self.bot_rsa_key_config.is_valid()

    @property
    def bdk_rsa_key_config(self):
        return self._bdk_rsa_key_config

    @property
    def bdk_certificate_config(self):
        return self._bdk_certificate_config
