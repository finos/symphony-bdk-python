import datetime
from unittest import mock

import pytest
from jwt import InvalidAudienceError

from symphony.bdk.core.auth.exception import AuthInitializationError
from symphony.bdk.core.auth.jwt_helper import create_signed_jwt, validate_jwt, create_signed_jwt_with_claims
from symphony.bdk.core.config.model.bdk_rsa_key_config import BdkRsaKeyConfig

AUDIENCE = "app-id"


@pytest.fixture(name="key_config")
def fixture_key_config():
    return BdkRsaKeyConfig()


@pytest.fixture(name="jwt_payload")
def fixture_jwt_payload():
    return {
        "sub": "bot-user",
        "exp": (datetime.datetime.now(datetime.timezone.utc).timestamp() + (5 * 60)),
        "aud": AUDIENCE
    }


def test_create_signed_jwt_from_path(key_config, rsa_key):
    private_key_path = "private_key_path/private_key.pem"
    key_config.path = private_key_path

    mock_open = mock.mock_open(read_data=rsa_key)

    with mock.patch('builtins.open', mock_open):
        assert create_signed_jwt(key_config, "test_bot") is not None
        mock_open.assert_called_with(private_key_path, "r")


def test_create_signed_jwt_from_content(key_config, rsa_key):
    key_config.content = rsa_key

    assert create_signed_jwt(key_config, "test_bot") is not None


def test_validate_jwt(jwt_payload, certificate, rsa_key):
    signed_jwt = create_signed_jwt_with_claims(rsa_key, jwt_payload)

    claims = validate_jwt(signed_jwt, certificate, AUDIENCE)
    assert claims == jwt_payload


def test_validate_jwt_with_wrong_audience(jwt_payload, certificate, rsa_key):
    signed_jwt = create_signed_jwt_with_claims(rsa_key, jwt_payload)

    with pytest.raises(InvalidAudienceError):
        validate_jwt(signed_jwt, certificate, "wrong audience")


def test_validate_jwt_with_invalid_cert(jwt_payload, rsa_key):
    signed_jwt = create_signed_jwt_with_claims(rsa_key, jwt_payload)

    with pytest.raises(AuthInitializationError):
        validate_jwt(signed_jwt, "invalid cert content", AUDIENCE)


def test_validate_jwt_with_invalid_jwt(certificate):
    with pytest.raises(AuthInitializationError):
        validate_jwt("invalid jwt", certificate, AUDIENCE)
