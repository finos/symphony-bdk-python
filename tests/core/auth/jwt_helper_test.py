import datetime
from unittest import mock

import pytest
from jwt import InvalidAudienceError

from symphony.bdk.core.auth.exception import AuthInitializationError
from symphony.bdk.core.auth.jwt_helper import (
    create_signed_jwt,
    create_signed_jwt_with_claims,
    extract_token_claims,
    validate_jwt,
)
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
        "aud": AUDIENCE,
    }


def test_create_signed_jwt_from_path(key_config, rsa_key):
    private_key_path = "private_key_path/private_key.pem"
    key_config.path = private_key_path

    mock_open = mock.mock_open(read_data=rsa_key)

    with mock.patch("builtins.open", mock_open):
        assert create_signed_jwt(key_config, "test_bot") is not None
        mock_open.assert_called_with(private_key_path, "r")


def test_create_signed_jwt_from_content(key_config, rsa_key):
    key_config.content = rsa_key

    assert create_signed_jwt(key_config, "test_bot") is not None


def test_validate_jwt(jwt_payload, certificate, rsa_key):
    signed_jwt = create_signed_jwt_with_claims(rsa_key, jwt_payload)

    claims = validate_jwt(signed_jwt, certificate, AUDIENCE)
    assert claims == jwt_payload


def test_validate_expired_jwt(jwt_payload, certificate, rsa_key):
    jwt_payload["exp"] = datetime.datetime.now(datetime.timezone.utc).timestamp() - 10
    signed_jwt = create_signed_jwt_with_claims(rsa_key, jwt_payload)

    with pytest.raises(AuthInitializationError):
        validate_jwt(signed_jwt, certificate, AUDIENCE)


def test_validate_jwt_with_empty_sub(jwt_payload, certificate, rsa_key):
    jwt_payload["sub"] = None
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


def test_extract_claims_from_valid_token(rsa_key):
    # Given: A valid jwt token
    payload = {"sub": "test-bot", "skd": True, "userId": 12345}
    token = create_signed_jwt_with_claims(rsa_key, payload)
    # When: extract JWT claims is called with a valid token
    claims = extract_token_claims(token)
    # Then: fields are extracted as expected
    assert claims["sub"] == "test-bot"
    assert claims["skd"] is True
    assert claims["userId"] == 12345


@pytest.mark.parametrize(
    "invalid_token",
    [
        # Given: invalid JWT to be extracted
        "not-a-jwt",
        "a.b.c",  # malformed JWT
        "a.b",  # not enough segments
        "",  # empty string
        None,  # None value
    ],
)
def test_extract_claims_from_invalid_token(invalid_token):
    # When: extract JWT claims is called
    claims = extract_token_claims(invalid_token)
    # Then: empty response is returned
    assert claims == {}
