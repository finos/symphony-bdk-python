from symphony.bdk.core.config.model.bdk_authentication_config import BdkAuthenticationConfig


def test_rsa_configuration():
    rsa_configuration = {"privateKey": {"path": "/path/to/bot/rsa-private-key.pem"}}
    authentication_config = BdkAuthenticationConfig(private_key_config=rsa_configuration.get("privateKey"))
    assert authentication_config.is_rsa_authentication_configured() is True
    assert authentication_config.is_rsa_authentication_configured() is True

    # Set up a non_empty content
    authentication_config.private_key.set_content(rsa_key_content="not_empty")
    assert authentication_config.is_rsa_authentication_configured() is True
    assert authentication_config.private_key._path is None, "rsa key path should have been overridden to None when " \
                                                            "setting non empty content "
    assert authentication_config.is_rsa_configuration_valid() is True

    # No content nor path
    authentication_config.private_key.set_content("")
    assert authentication_config.is_rsa_authentication_configured() is False
    assert authentication_config.is_rsa_configuration_valid() is False


def test_certificate_configuration():
    certificate_configuration = {"certificate": {"path": "/path/to/bot-certificate.p12", "password": "changeit"}}
    authentication_config = BdkAuthenticationConfig(certificate_config=certificate_configuration.get("certificate"))
    assert authentication_config.is_certificate_authentication_configured() is True
    assert authentication_config.is_certificate_configuration_valid() is True

    # Non empty content
    authentication_config.certificate.set_content(certificate_content="non_empty")
    assert authentication_config.is_certificate_authentication_configured() is True
    assert authentication_config.certificate._path is None, "certificate path should have been overridden to None " \
                                                            "when setting non empty content "
    assert authentication_config.is_certificate_configuration_valid() is True

    # Keep the content and remove the certificate path
    authentication_config.certificate.set_path(certificate_path=None)
    assert authentication_config.is_certificate_authentication_configured() is True
    assert authentication_config.is_certificate_configuration_valid() is True

    # No password with path
    authentication_config.certificate.set_path(certificate_path="/path/to/bot-certificate.p12")
    authentication_config.certificate.password = None
    assert authentication_config.is_certificate_authentication_configured() is False
    assert authentication_config.is_certificate_configuration_valid() is False

    # No password with certificate
    authentication_config.certificate.set_path(certificate_path=None)
    authentication_config.certificate.set_content(certificate_content="not_empty")
    assert authentication_config.is_certificate_authentication_configured() is False
    assert authentication_config.is_certificate_configuration_valid() is False
