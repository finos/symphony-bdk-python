from unittest.mock import AsyncMock, patch

import pytest

from symphony.bdk.core.auth.obo_authenticator import (
    OboAuthenticatorCert,
    OboAuthenticatorRsa,
)
from symphony.bdk.core.config.model.bdk_app_config import BdkAppConfig
from symphony.bdk.gen.auth_model.obo_auth_response import OboAuthResponse
from symphony.bdk.gen.exceptions import ApiException
from symphony.bdk.gen.login_model.authenticate_request import AuthenticateRequest
from symphony.bdk.gen.login_model.token import Token
from tests.core.config import minimal_retry_config


@pytest.fixture(name="config")
def fixture_config():
    app_config = {"appId": "test_bot", "privateKey": {"path": "path/to/private_key"}}
    return BdkAppConfig(app_config)


@pytest.mark.asyncio
async def test_obo_session_username(config):
    signed_jwt = "signed_jwt"
    app_token = "app_token"
    session_token = "session_token"
    username = "username"

    with (
        patch(
            "symphony.bdk.core.auth.obo_authenticator.create_signed_jwt",
            return_value=signed_jwt,
        ) as create_jwt,
        patch("symphony.bdk.core.auth.obo_authenticator.AuthenticationApi") as auth_api,
    ):
        auth_api.pubkey_app_authenticate_post = AsyncMock(
            return_value=Token(token=app_token)
        )
        auth_api.pubkey_app_username_username_authenticate_post = AsyncMock(
            return_value=Token(token=session_token)
        )

        obo_authenticator = OboAuthenticatorRsa(
            config, auth_api, minimal_retry_config()
        )
        retrieved_session_token = (
            await obo_authenticator.retrieve_obo_session_token_by_username(username)
        )

        assert retrieved_session_token == session_token
        create_jwt.assert_called_once_with(config.private_key, config.app_id)
        auth_api.pubkey_app_authenticate_post.assert_called_once_with(
            AuthenticateRequest(token=signed_jwt)
        )
        auth_api.pubkey_app_username_username_authenticate_post.assert_called_once_with(
            session_token=app_token, username=username
        )


@pytest.mark.asyncio
async def test_obo_session_user_id(config):
    signed_jwt = "signed_jwt"
    app_token = "app_token"
    session_token = "session_token"
    user_id = 1234

    with (
        patch(
            "symphony.bdk.core.auth.obo_authenticator.create_signed_jwt",
            return_value=signed_jwt,
        ) as create_jwt,
        patch("symphony.bdk.core.auth.obo_authenticator.AuthenticationApi") as auth_api,
    ):
        auth_api.pubkey_app_authenticate_post = AsyncMock(
            return_value=Token(token=app_token)
        )
        auth_api.pubkey_app_user_user_id_authenticate_post = AsyncMock(
            return_value=Token(token=session_token)
        )

        obo_authenticator = OboAuthenticatorRsa(
            config, auth_api, minimal_retry_config()
        )
        retrieved_session_token = (
            await obo_authenticator.retrieve_obo_session_token_by_user_id(user_id)
        )

        assert retrieved_session_token == session_token
        create_jwt.assert_called_once_with(config.private_key, config.app_id)
        auth_api.pubkey_app_authenticate_post.assert_called_once_with(
            AuthenticateRequest(token=signed_jwt)
        )
        auth_api.pubkey_app_user_user_id_authenticate_post.assert_called_once_with(
            session_token=app_token, user_id=user_id
        )


@pytest.mark.asyncio
async def test_api_exception(config):
    with (
        patch(
            "symphony.bdk.core.auth.obo_authenticator.create_signed_jwt",
            return_value="signed_jwt",
        ),
        patch("symphony.bdk.core.auth.obo_authenticator.AuthenticationApi") as auth_api,
    ):
        auth_api.pubkey_app_authenticate_post = AsyncMock(side_effect=ApiException(400))

        obo_authenticator = OboAuthenticatorRsa(
            config, auth_api, minimal_retry_config()
        )

        with pytest.raises(ApiException):
            await obo_authenticator.retrieve_obo_session_token_by_username("username")

        with pytest.raises(ApiException):
            await obo_authenticator.retrieve_obo_session_token_by_user_id(1234)


@pytest.mark.asyncio
async def test_api_exception_in_authenticate_username(config):
    with (
        patch(
            "symphony.bdk.core.auth.obo_authenticator.create_signed_jwt",
            return_value="signed_jwt",
        ),
        patch("symphony.bdk.core.auth.obo_authenticator.AuthenticationApi") as auth_api,
    ):
        auth_api.pubkey_app_authenticate_post = AsyncMock(
            return_value=Token(token="app_token")
        )
        auth_api.pubkey_app_username_username_authenticate_post = AsyncMock(
            side_effect=ApiException(400)
        )

        obo_authenticator = OboAuthenticatorRsa(
            config, auth_api, minimal_retry_config()
        )

        with pytest.raises(ApiException):
            await obo_authenticator.retrieve_obo_session_token_by_username("username")


@pytest.mark.asyncio
async def test_api_exception_in_authenticate_userid(config):
    with (
        patch(
            "symphony.bdk.core.auth.obo_authenticator.create_signed_jwt",
            return_value="signed_jwt",
        ),
        patch("symphony.bdk.core.auth.obo_authenticator.AuthenticationApi") as auth_api,
    ):
        auth_api.pubkey_app_authenticate_post = AsyncMock(
            return_value=Token(token="app_token")
        )
        auth_api.pubkey_app_user_user_id_authenticate_post = AsyncMock(
            side_effect=ApiException(400)
        )

        obo_authenticator = OboAuthenticatorRsa(
            config, auth_api, minimal_retry_config()
        )

        with pytest.raises(ApiException):
            await obo_authenticator.retrieve_obo_session_token_by_user_id(1234)


@pytest.mark.asyncio
async def test_authenticate_by_username(config):
    signed_jwt = "signed_jwt"
    app_token = "app_token"
    session_token = "session_token"
    username = "username"

    with (
        patch(
            "symphony.bdk.core.auth.obo_authenticator.create_signed_jwt",
            return_value=signed_jwt,
        ) as create_jwt,
        patch("symphony.bdk.core.auth.obo_authenticator.AuthenticationApi") as auth_api,
    ):
        auth_api.pubkey_app_authenticate_post = AsyncMock(
            return_value=Token(token=app_token)
        )
        auth_api.pubkey_app_username_username_authenticate_post = AsyncMock(
            return_value=Token(token=session_token)
        )

        obo_authenticator = OboAuthenticatorRsa(
            config, auth_api, minimal_retry_config()
        )
        obo_session = obo_authenticator.authenticate_by_username(username)

        assert await obo_session.session_token == session_token
        create_jwt.assert_called_once_with(config.private_key, config.app_id)
        auth_api.pubkey_app_authenticate_post.assert_called_once_with(
            AuthenticateRequest(token=signed_jwt)
        )
        auth_api.pubkey_app_username_username_authenticate_post.assert_called_once_with(
            session_token=app_token, username=username
        )


@pytest.mark.asyncio
async def test_authenticate_by_user_id(config):
    signed_jwt = "signed_jwt"
    app_token = "app_token"
    session_token = "session_token"
    user_id = 1234

    with (
        patch(
            "symphony.bdk.core.auth.obo_authenticator.create_signed_jwt",
            return_value=signed_jwt,
        ) as create_jwt,
        patch("symphony.bdk.core.auth.obo_authenticator.AuthenticationApi") as auth_api,
    ):
        auth_api.pubkey_app_authenticate_post = AsyncMock(
            return_value=Token(token=app_token)
        )
        auth_api.pubkey_app_user_user_id_authenticate_post = AsyncMock(
            return_value=Token(token=session_token)
        )

        obo_authenticator = OboAuthenticatorRsa(
            config, auth_api, minimal_retry_config()
        )
        obo_session = obo_authenticator.authenticate_by_user_id(1234)

        assert await obo_session.session_token == "session_token"
        create_jwt.assert_called_once_with(config.private_key, config.app_id)
        auth_api.pubkey_app_authenticate_post.assert_called_once_with(
            AuthenticateRequest(token=signed_jwt)
        )
        auth_api.pubkey_app_user_user_id_authenticate_post.assert_called_once_with(
            session_token=app_token, user_id=user_id
        )


@pytest.mark.asyncio
async def test_obo_session_username_cert_authentication():
    with patch(
        "symphony.bdk.core.auth.obo_authenticator.CertificateAuthenticationApi"
    ) as auth_api:
        username = "username"
        app_token = "app_token"
        session_token = "session_token"

        auth_api.v1_app_authenticate_post = AsyncMock(
            return_value=Token(token=app_token)
        )
        auth_api.v1_app_username_username_authenticate_post = AsyncMock(
            return_value=OboAuthResponse(session_token=session_token)
        )

        obo_authenticator = OboAuthenticatorCert(auth_api, minimal_retry_config())
        retrieved_session_token = (
            await obo_authenticator.retrieve_obo_session_token_by_username(username)
        )

        assert retrieved_session_token == session_token
        auth_api.v1_app_authenticate_post.assert_called_once()
        auth_api.v1_app_username_username_authenticate_post.assert_called_once_with(
            session_token=app_token, username=username
        )


@pytest.mark.asyncio
async def test_obo_session_user_id_cert_authentication():
    with patch(
        "symphony.bdk.core.auth.obo_authenticator.CertificateAuthenticationApi"
    ) as auth_api:
        user_id = 1234
        app_token = "app_token"
        session_token = "session_token"

        auth_api.v1_app_authenticate_post = AsyncMock(
            return_value=Token(token=app_token)
        )
        auth_api.v1_app_user_uid_authenticate_post = AsyncMock(
            return_value=OboAuthResponse(session_token=session_token)
        )

        obo_authenticator = OboAuthenticatorCert(auth_api, minimal_retry_config())
        retrieved_session_token = (
            await obo_authenticator.retrieve_obo_session_token_by_user_id(user_id)
        )

        assert retrieved_session_token == session_token
        auth_api.v1_app_authenticate_post.assert_called_once()
        auth_api.v1_app_user_uid_authenticate_post.assert_called_once_with(
            session_token=app_token, uid=user_id
        )


@pytest.mark.asyncio
async def test_api_exception_cert_auth_in_app_authenticate():
    with patch(
        "symphony.bdk.core.auth.obo_authenticator.CertificateAuthenticationApi"
    ) as auth_api:
        auth_api.v1_app_authenticate_post = AsyncMock(side_effect=ApiException(400))
        obo_authenticator = OboAuthenticatorCert(auth_api, minimal_retry_config())

        with pytest.raises(ApiException):
            await obo_authenticator.retrieve_obo_session_token_by_username("username")

        with pytest.raises(ApiException):
            await obo_authenticator.retrieve_obo_session_token_by_user_id(1234)


@pytest.mark.asyncio
async def test_api_exception_cert_auth_in_username_authenticate():
    with patch(
        "symphony.bdk.core.auth.obo_authenticator.CertificateAuthenticationApi"
    ) as auth_api:
        auth_api.v1_app_authenticate_post = AsyncMock(
            return_value=Token(token="app_token")
        )
        auth_api.v1_app_username_username_authenticate_post = AsyncMock(
            side_effect=ApiException(400)
        )
        obo_authenticator = OboAuthenticatorCert(auth_api, minimal_retry_config())

        with pytest.raises(ApiException):
            await obo_authenticator.retrieve_obo_session_token_by_username("username")


@pytest.mark.asyncio
async def test_api_exception_cert_auth_in_userid_authenticate():
    with patch(
        "symphony.bdk.core.auth.obo_authenticator.CertificateAuthenticationApi"
    ) as auth_api:
        auth_api.v1_app_authenticate_post = AsyncMock(
            return_value=Token(token="app_token")
        )
        auth_api.v1_app_user_uid_authenticate_post = AsyncMock(
            side_effect=ApiException(400)
        )
        obo_authenticator = OboAuthenticatorCert(auth_api, minimal_retry_config())

        with pytest.raises(ApiException):
            await obo_authenticator.retrieve_obo_session_token_by_user_id(1234)


@pytest.mark.asyncio
async def test_authenticate_by_username_cert_authentication():
    with patch(
        "symphony.bdk.core.auth.obo_authenticator.CertificateAuthenticationApi"
    ) as auth_api:
        username = "username"
        app_token = "app_token"
        session_token = "session_token"

        auth_api.v1_app_authenticate_post = AsyncMock(
            return_value=Token(token=app_token)
        )
        auth_api.v1_app_username_username_authenticate_post = AsyncMock(
            return_value=OboAuthResponse(session_token=session_token)
        )

        obo_authenticator = OboAuthenticatorCert(auth_api, minimal_retry_config())
        obo_session = obo_authenticator.authenticate_by_username(username)

        assert obo_session.username == username
        assert await obo_session.session_token == session_token
        auth_api.v1_app_authenticate_post.assert_called_once()
        auth_api.v1_app_username_username_authenticate_post.assert_called_once_with(
            session_token=app_token, username=username
        )


@pytest.mark.asyncio
async def test_authenticate_by_user_id_cert_authentication():
    with patch(
        "symphony.bdk.core.auth.obo_authenticator.CertificateAuthenticationApi"
    ) as auth_api:
        user_id = 1234
        app_token = "app_token"
        session_token = "session_token"

        auth_api.v1_app_authenticate_post = AsyncMock(
            return_value=Token(token=app_token)
        )
        auth_api.v1_app_user_uid_authenticate_post = AsyncMock(
            return_value=OboAuthResponse(session_token=session_token)
        )

        obo_authenticator = OboAuthenticatorCert(auth_api, minimal_retry_config())
        obo_session = obo_authenticator.authenticate_by_user_id(user_id)

        assert obo_session.user_id == user_id
        assert await obo_session.session_token == session_token
        auth_api.v1_app_authenticate_post.assert_called_once()
        auth_api.v1_app_user_uid_authenticate_post.assert_called_once_with(
            session_token=app_token, uid=user_id
        )
