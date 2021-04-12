from unittest.mock import AsyncMock, patch

import pytest

from symphony.bdk.core.auth.auth_session import AppAuthSession
from symphony.bdk.core.auth.exception import AuthInitializationError
from symphony.bdk.core.auth.ext_app_authenticator import ExtensionAppAuthenticatorRsa
from symphony.bdk.core.auth.tokens_repository import InMemoryTokensRepository
from symphony.bdk.core.config.model.bdk_rsa_key_config import BdkRsaKeyConfig
from symphony.bdk.gen import ApiException
from symphony.bdk.gen.login_model.extension_app_tokens import ExtensionAppTokens
from symphony.bdk.gen.pod_model.pod_certificate import PodCertificate


@pytest.fixture(name="ext_app_authenticator")
def fixture_ext_app_authenticator():
    return new_ext_app_authenticator()


def new_ext_app_authenticator():
    return ExtensionAppAuthenticatorRsa(None, None, None, None)


@pytest.mark.asyncio
async def test_authenticate_extension_app_calls_refresh():
    with patch("symphony.bdk.core.auth.ext_app_authenticator.AppAuthSession.refresh") as mock_refresh:
        ext_app_authenticator = new_ext_app_authenticator()

        auth_session = await ext_app_authenticator.authenticate_extension_app("app_token")
        assert auth_session is not None
        mock_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_authenticate_extension_app(ext_app_authenticator):
    app_token = "app_token"
    retrieved_app_token = "out_app_token"
    symphony_token = "sym_token"
    tokens = ExtensionAppTokens(app_id="app_id", app_token=retrieved_app_token, symphony_token=symphony_token,
                                expire_at=12345)
    ext_app_authenticator.authenticate_and_retrieve_tokens = AsyncMock(return_value=tokens)

    auth_session = await ext_app_authenticator.authenticate_extension_app(app_token)

    assert auth_session is not None
    assert isinstance(auth_session, AppAuthSession)
    ext_app_authenticator.authenticate_and_retrieve_tokens.assert_awaited_once_with(app_token)


@pytest.mark.asyncio
async def test_authenticate_and_retrieve_tokens():
    with patch("symphony.bdk.core.auth.ext_app_authenticator.create_signed_jwt") as mock_create_jwt:
        signed_jwt = "signed jwt"
        app_token = "app_token"
        app_id = "app_id"
        out_app_token = "out_app_token"
        symphony_token = "symphony_token"
        key_config = BdkRsaKeyConfig(content="key content")

        mock_create_jwt.return_value = signed_jwt
        extension_app_tokens = ExtensionAppTokens(app_id="my_app_id", app_token=out_app_token,
                                                  symphony_token=symphony_token,
                                                  expire_at=12345)
        mock_authentication_api = AsyncMock()
        mock_authentication_api.v1_pubkey_app_authenticate_extension_app_post = AsyncMock(
            return_value=extension_app_tokens)

        extension_app_authenticator = ExtensionAppAuthenticatorRsa(mock_authentication_api, None, app_id, key_config)
        returned_ext_app_tokens = await extension_app_authenticator.authenticate_and_retrieve_tokens(app_token)

        assert returned_ext_app_tokens == extension_app_tokens
        assert extension_app_authenticator._tokens_repository._tokens == {out_app_token: symphony_token}
        assert await extension_app_authenticator.is_token_pair_valid(out_app_token, symphony_token)
        assert not await extension_app_authenticator.is_token_pair_valid("invalid app token", symphony_token)
        assert not await extension_app_authenticator.is_token_pair_valid(out_app_token, "invalid symphony token")

        mock_create_jwt.assert_called_once_with(key_config, app_id)
        mock_authentication_api.v1_pubkey_app_authenticate_extension_app_post.assert_called_once()

        call_args = mock_authentication_api.v1_pubkey_app_authenticate_extension_app_post.call_args.args[0]
        assert call_args.app_token == app_token
        assert call_args.auth_token == signed_jwt


@pytest.mark.asyncio
async def test_authenticate_and_retrieve_tokens_failure():
    with patch("symphony.bdk.core.auth.ext_app_authenticator.create_signed_jwt") as mock_create_jwt:
        key_config = BdkRsaKeyConfig(content="key content")
        mock_create_jwt.return_value = "signed jwt"

        mock_authentication_api = AsyncMock()
        mock_authentication_api.v1_pubkey_app_authenticate_extension_app_post = AsyncMock(side_effect=ValueError)

        extension_app_authenticator = ExtensionAppAuthenticatorRsa(mock_authentication_api, None, "app_id", key_config)
        with pytest.raises(ValueError):
            await extension_app_authenticator.authenticate_and_retrieve_tokens("app_token")

        assert extension_app_authenticator._tokens_repository._tokens == {}
        mock_authentication_api.v1_pubkey_app_authenticate_extension_app_post.assert_called_once()


@pytest.mark.asyncio
async def test_validate_jwt_get_pod_certificate_failure():
    with patch("symphony.bdk.core.auth.ext_app_authenticator.validate_jwt") as mock_validate:
        mock_pod_api = AsyncMock()
        mock_pod_api.v1_podcert_get = AsyncMock(side_effect=ApiException(status=501))

        with pytest.raises(AuthInitializationError):
            ext_app_authenticator = ExtensionAppAuthenticatorRsa(None, mock_pod_api, "app-id", None)
            await ext_app_authenticator.validate_jwt("my-jwt")

        mock_pod_api.v1_podcert_get.assert_called_once()
        mock_validate.assert_not_called()


@pytest.mark.asyncio
async def test_validate_jwt():
    with patch("symphony.bdk.core.auth.ext_app_authenticator.validate_jwt") as mock_validate:
        certificate_content = "certificate content"
        jwt = "my-jwt"
        app_id = "app-id"

        mock_pod_api = AsyncMock()
        mock_pod_api.v1_podcert_get = AsyncMock(return_value=PodCertificate(certificate=certificate_content))

        ext_app_authenticator = ExtensionAppAuthenticatorRsa(None, mock_pod_api, app_id, None)

        await ext_app_authenticator.validate_jwt(jwt)
        mock_pod_api.v1_podcert_get.assert_called_once()
        mock_validate.assert_called_once_with(jwt, certificate_content, app_id)
