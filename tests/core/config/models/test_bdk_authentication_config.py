from symphony.bdk.core.config.model.bdk_authentication_config import BdkAuthenticationConfig


def test_rsa_configuration():
    rsa_configuration = {"privateKey": {"path": "/path/to/bot/rsa-private-key.pem"}}
    authentication_config = BdkAuthenticationConfig(private_key_config=rsa_configuration.get("privateKey"))
    assert authentication_config.is_rsa_authentication_configured() is True

    # Set up a non_empty content
    authentication_config.private_key.content = "not_empty"
    assert authentication_config.is_rsa_authentication_configured() is True
    assert authentication_config.is_rsa_configuration_valid() is True

    # Keep the content and remove the key path
    authentication_config.private_key.path = None
    assert authentication_config.is_rsa_authentication_configured() is True
    assert authentication_config.is_rsa_configuration_valid() is False


def test_certificate_configuration():
    certificate_configuration = {"certificate": {"path": "/path/to/bot-certificate.p12", "password": "changeit"}}
    authentication_config = BdkAuthenticationConfig(certificate_config=certificate_configuration.get("certificate"))
    assert authentication_config.is_certificate_authentication_configured() is True
    assert authentication_config.is_certificate_configuration_valid() is False

    # Non empty content
    authentication_config.certificate.content = "non_empty"
    assert authentication_config.is_certificate_authentication_configured() is True
    assert authentication_config.is_certificate_configuration_valid() is True

    # Keep the content and remove the certificate path
    authentication_config.certificate.path = None
    assert authentication_config.is_certificate_authentication_configured() is True
    assert authentication_config.is_certificate_configuration_valid() is False

    # No password provided
    authentication_config.certificate.path = "/path/to/bot-certificate.p12"
    authentication_config.certificate.password = None
    assert authentication_config.is_certificate_authentication_configured() is False
    assert authentication_config.is_certificate_configuration_valid() is False
