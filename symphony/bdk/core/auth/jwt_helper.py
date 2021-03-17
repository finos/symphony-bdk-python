import datetime
from cryptography.x509 import load_pem_x509_certificate

from jose import jwt

from symphony.bdk.core.config.model.bdk_rsa_key_config import BdkRsaKeyConfig

RS512 = "RS512"

DEFAULT_EXPIRATION = 290


def create_signed_jwt(private_key_config: BdkRsaKeyConfig, username: str, expiration: int = None) -> str:
    """Creates a JWT with the provided user name and expiration date, signed with the provided private key.

    :param private_key_config:  The private key configuration for a service account or an extension app.
    :param username:            The username of the user to authenticate
    :param expiration:          Expiration of the authentication request in seconds.
                                By default the signed jwt will be valid in maximum 290 seconds (4min 50s)
                                which is the maximum expiration accepted by the Symphony backend.

    :return: a signed JWT for a specific user or an extension app.
    """
    private_key = private_key_config.get_private_key_content()
    expiration = expiration if expiration is not None else int(
        datetime.datetime.now(datetime.timezone.utc).timestamp() + DEFAULT_EXPIRATION)
    payload = {
        "sub": username,
        "exp": expiration
    }
    return jwt.encode(payload, private_key, algorithm=RS512)


def validate_jwt(jwt_token: str, certificate: str) -> dict:
    """Validate a jwt against a X509 certificate in pem format and returns the jwt claims.

    :param jwt_token: the token to be validated
    :param certificate: the X509 certificate in pem format to be used for jwt validation
    :return: a dictionary containing the jwt claims
    :raise JWTError: If the signature is invalid in any way.
    :raise ExpiredSignatureError: If the signature has expired.
    :raise JWTClaimsError: If any claim is invalid in any way.
    """
    public_key = load_pem_x509_certificate(certificate).public_key()
    return jwt.decode(jwt_token, public_key, algorithms=[RS512])
