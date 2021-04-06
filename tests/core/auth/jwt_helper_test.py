import datetime

import pytest
from jwt import InvalidAudienceError

from symphony.bdk.core.auth.exception import AuthInitializationError
from symphony.bdk.core.auth.jwt_helper import create_signed_jwt, validate_jwt, create_signed_jwt_with_claims
from symphony.bdk.core.config.model.bdk_rsa_key_config import BdkRsaKeyConfig
from tests.utils.resource_utils import get_resource_filepath, get_resource_content

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


def test_create_signed_jwt_from_path(key_config):
    key_config.path = get_resource_filepath("key/private_key.pem")

    assert create_signed_jwt(key_config, "test_bot") is not None


def test_create_signed_jwt_from_content(key_config):
    key_config.content = get_resource_content("key/private_key.pem")

    assert create_signed_jwt(key_config, "test_bot") is not None


def test_create_signed_jwt(key_config):
    key_config.content = get_resource_content("key/private_key.pem")
    key_config.path = get_resource_filepath("key/private_key.pem")

    assert key_config._content is None
    assert key_config._path is not None
    assert create_signed_jwt(key_config, "test_bot") is not None


def test_validate_jwt(jwt_payload):
    signed_jwt = create_signed_jwt_with_claims(get_resource_content("key/private_key_from_cert.pem"), jwt_payload)

    claims = validate_jwt(signed_jwt, get_resource_content("cert/certificate_from_private_key.cert"), AUDIENCE)
    assert claims == jwt_payload


def test_validate_jwt_with_wrong_audience(jwt_payload):
    signed_jwt = create_signed_jwt_with_claims(get_resource_content("key/private_key_from_cert.pem"), jwt_payload)

    with pytest.raises(InvalidAudienceError):
        validate_jwt(signed_jwt, get_resource_content("cert/certificate_from_private_key.cert"), "wrong audience")


def test_validate_jwt_with_invalid_cert(jwt_payload):
    with pytest.raises(AuthInitializationError):
        signed_jwt = create_signed_jwt_with_claims(get_resource_content("key/private_key_from_cert.pem"), jwt_payload)
        validate_jwt(signed_jwt, "invalid cert content", AUDIENCE)


def test_validate_jwt_with_invalid_jwt():
    with pytest.raises(AuthInitializationError):
        validate_jwt("invalid jwt", get_resource_content("cert/certificate_from_private_key.cert"), AUDIENCE)
