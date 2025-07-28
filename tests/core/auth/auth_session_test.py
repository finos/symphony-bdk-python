from datetime import datetime, timezone

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from symphony.bdk.core.auth.auth_session import (
    AuthSession,
    OboAuthSession,
    AppAuthSession,
    SKD_FLAG_NAME,
)
from symphony.bdk.core.auth.exception import AuthInitializationError
from symphony.bdk.gen.login_model.token import Token
from symphony.bdk.gen.login_model.extension_app_tokens import ExtensionAppTokens
from symphony.bdk.core.auth.bot_authenticator import BotAuthenticatorRsa
from symphony.bdk.core.config.model.bdk_bot_config import BdkBotConfig
from symphony.bdk.gen.api_client import ApiClient

@pytest.fixture
def mock_authenticator():

    config = MagicMock(spec=BdkBotConfig)
    login_client = MagicMock(spec=ApiClient)
    relay_client = MagicMock(spec=ApiClient)
    retry_config = MagicMock()
    authenticator = BotAuthenticatorRsa(config, login_client, relay_client, retry_config)
    authenticator.retrieve_session_token = AsyncMock(return_value="session_token_string")
    authenticator.retrieve_key_manager_token = AsyncMock(return_value="km_token_string")
    authenticator.agent_version_service = AsyncMock()
    return authenticator


@pytest.fixture
def auth_session(mock_authenticator):
    return AuthSession(mock_authenticator)


@pytest.mark.asyncio
async def test_refresh():
    mock_bot_authenticator = AsyncMock()
    mock_bot_authenticator.retrieve_session_token.return_value = "session_token"
    mock_bot_authenticator.retrieve_key_manager_token.return_value = "km_token"

    auth_session = AuthSession(mock_bot_authenticator)
    await auth_session.refresh()
    assert await auth_session.session_token == "session_token"
    assert await auth_session.key_manager_token == "km_token"


@pytest.mark.asyncio
async def test_auth_token():
    mock_bot_authenticator = AsyncMock()
    expired_ts, fresh_ts, = (
        datetime.now(timezone.utc).timestamp(),
        datetime.now(timezone.utc).timestamp() + 500,
    )
    mock_bot_authenticator.retrieve_session_token_object.side_effect = [
        (
            Token(
                authorization_token="initial_token",
                token="session_tokeт",
                name="sessionToken",
            ),
            expired_ts,
        ),
        (
            Token(
                authorization_token="updated_token",
                token="session_token",
                name="sessionToken",
            ),
            fresh_ts,
        ),
    ]
    auth_session = AuthSession(mock_bot_authenticator)
    assert await auth_session.auth_token == "initial_token"
    assert await auth_session.auth_token == "updated_token"
    assert await auth_session.auth_token == "updated_token"
    assert mock_bot_authenticator.retrieve_session_token_object.call_count == 2


@pytest.mark.asyncio
async def test_refresh_obo():
    mock_obo_authenticator = AsyncMock()
    mock_obo_authenticator.retrieve_obo_session_token_by_user_id.side_effect = [
        "session_token1",
        "session_token2",
    ]
    mock_obo_authenticator.retrieve_obo_session_token_by_username.side_effect = [
        "session_token3",
        "session_token4",
    ]

    obo_session = OboAuthSession(mock_obo_authenticator, user_id=1234)

    assert await obo_session.session_token == "session_token1"
    assert await obo_session.key_manager_token == ""

    await obo_session.refresh()
    assert await obo_session.session_token == "session_token2"
    assert await obo_session.key_manager_token == ""

    obo_session = OboAuthSession(mock_obo_authenticator, username="username")

    assert await obo_session.session_token == "session_token3"
    assert await obo_session.key_manager_token == ""

    await obo_session.refresh()
    assert await obo_session.session_token == "session_token4"
    assert await obo_session.key_manager_token == ""


def test_obo_init_failed():
    with pytest.raises(AuthInitializationError):
        OboAuthSession(None, user_id=1234, username="username")

    with pytest.raises(AuthInitializationError):
        OboAuthSession(None)


@pytest.mark.asyncio
async def test_app_auth_session():
    input_app_token = "input_app_token"
    retrieved_app_token = "my_app_token"
    symphony_token = "my_symphony_token"
    expire_at = 1539636528288

    ext_app_authenticator = AsyncMock()
    ext_app_authenticator.authenticate_and_retrieve_tokens.return_value = (
        ExtensionAppTokens(
            app_id="app_id",
            app_token=retrieved_app_token,
            symphony_token=symphony_token,
            expire_at=expire_at,
        )
    )

    session = AppAuthSession(ext_app_authenticator, input_app_token)
    await session.refresh()

    ext_app_authenticator.authenticate_and_retrieve_tokens.assert_called_once_with(
        input_app_token
    )
    assert session.app_token == retrieved_app_token
    assert session.symphony_token == symphony_token
    assert session.expire_at == expire_at


@pytest.mark.asyncio
async def test_skd_disabled_if_claim_is_missing(auth_session):
    # Given: The token claims do not contain the SKD flag
    with patch(
        "symphony.bdk.core.auth.auth_session.extract_token_claims", return_value={}
    ):
        # When: skd_enabled is checked
        is_enabled = await auth_session.skd_enabled
        # Then: The result is False
        assert is_enabled is False


@pytest.mark.asyncio
async def test_skd_disabled_if_agent_not_supported(auth_session, mock_authenticator):
    # Given: The token has the SKD flag but the agent does not support it
    mock_authenticator.agent_version_service.is_skd_supported.return_value = False
    claims_with_skd = {SKD_FLAG_NAME: True}
    with patch(
        "symphony.bdk.core.auth.auth_session.extract_token_claims",
        return_value=claims_with_skd,
    ):
        # When: skd_enabled is checked
        is_enabled = await auth_session.skd_enabled
        # Then: The result is False and the agent version was checked
        assert is_enabled is False
        mock_authenticator.agent_version_service.is_skd_supported.assert_called_once()


@pytest.mark.asyncio
async def test_skd_enabled_when_fully_supported(auth_session, mock_authenticator):
    # Given: The token has the SKD flag AND the agent supports it
    mock_authenticator.agent_version_service.is_skd_supported.return_value = True
    claims_with_skd = {SKD_FLAG_NAME: True}
    with patch(
        "symphony.bdk.core.auth.auth_session.extract_token_claims",
        return_value=claims_with_skd,
    ):
        # When: skd_enabled is checked
        is_enabled = await auth_session.skd_enabled
        # Then: The result is True and the agent version was checked
        assert is_enabled is True
        mock_authenticator.agent_version_service.is_skd_supported.assert_called_once()


@pytest.mark.asyncio
async def test_km_token_is_empty_when_skd_enabled(auth_session, mock_authenticator):
    # Given: SKD is fully enabled
    mock_authenticator.agent_version_service.is_skd_supported.return_value = True
    claims_with_skd = {SKD_FLAG_NAME: True}
    with patch(
        "symphony.bdk.core.auth.auth_session.extract_token_claims",
        return_value=claims_with_skd,
    ):
        # When: The key manager token is requested
        km_token = await auth_session.key_manager_token
        # Then: The token is an empty string and the real retrieval method was NOT called
        assert km_token == ""
        mock_authenticator.retrieve_key_manager_token.assert_not_called()


@pytest.mark.asyncio
async def test_km_token_is_retrieved_when_skd_disabled(
    auth_session, mock_authenticator
):
    # Given: SKD is disabled because the token claim is missing
    with patch(
        "symphony.bdk.core.auth.auth_session.extract_token_claims", return_value={}
    ):
        # When: The key manager token is requested
        km_token = await auth_session.key_manager_token
        # Then: The real token is returned and the retrieval method was called
        assert km_token == "km_token_string"
        mock_authenticator.retrieve_key_manager_token.assert_called_once()
