"""Module to help with jwt handling.
"""
import datetime

import jwt
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.x509 import load_pem_x509_certificate

from symphony.bdk.core.auth.exception import AuthInitializationError
from symphony.bdk.core.config.model.bdk_rsa_key_config import BdkRsaKeyConfig

JWT_ENCRYPTION_ALGORITHM = "RS512"

DEFAULT_EXPIRATION_SECONDS = (5 * 50) - 10


def create_signed_jwt(private_key_config: BdkRsaKeyConfig, username: str, expiration: int = None) -> str:
    """Creates a JWT with the provided user name and expiration date, signed with the provided private key.

    :param private_key_config:  The private key configuration for a service account or an extension app.
    :param username:            The username of the user to authenticate.
    :param expiration:          Expiration of the authentication request in seconds.
                                By default the signed jwt will be valid in maximum 290 seconds (4min 50s)
                                which is the maximum expiration accepted by the Symphony backend.

    :return: a signed JWT for a specific user or an extension app.
    """
    expiration = expiration if expiration is not None else int(
        datetime.datetime.now(datetime.timezone.utc).timestamp() + DEFAULT_EXPIRATION_SECONDS)
    payload = {
        "sub": username,
        "exp": expiration
    }
    return create_signed_jwt_with_claims(private_key_config.get_private_key_content(), payload)


def create_signed_jwt_with_claims(private_key: str, payload: dict) -> str:
    """Creates a JWT with the payload signed with the provided private key content.
    For testing purposes only.

    :param private_key: the privste key content in string format.
    :param payload: the payload (aka claims) of the JWT in dict format.
    :return: a signed JWT
    """
    return jwt.encode(payload, private_key, algorithm=JWT_ENCRYPTION_ALGORITHM)


def validate_jwt(jwt_token: str, certificate: str, allowed_audience: str) -> dict:
    """Validate a jwt against a X509 certificate in pem format and returns the jwt claims.

    :param jwt_token: the token to be validated
    :param certificate: the X509 certificate in pem format to be used for jwt validation
    :param allowed_audience: the expected value in "aud" claim. If it doesn't match jwt will be rejected
    :return: a dictionary containing the jwt claims
    :raise AuthInitializationError: If the certificate or jwt are invalid.
    """
    try:
        return jwt.decode(jwt_token, _parse_public_key_from_x509_cert(certificate),
                          algorithms=[JWT_ENCRYPTION_ALGORITHM], audience=allowed_audience)
    except (jwt.DecodeError, jwt.ExpiredSignatureError) as exc:
        raise AuthInitializationError("Unable to validate the jwt") from exc


def _parse_public_key_from_x509_cert(certificate: str) -> str:
    """Returns the public key in PEM format given a X509 certificate content in PEM format

    :param certificate: the X509 certificate in PEM format
    :return: the public key associated to the certificate in PEM format
    """
    try:
        public_key = load_pem_x509_certificate(certificate.encode()).public_key()
        return public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode()
    except ValueError as exc:
        raise AuthInitializationError("Unable to parse the certificate. Check certificate format.") from exc
