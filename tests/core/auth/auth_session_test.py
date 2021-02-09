from unittest.mock import AsyncMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession, OboAuthSession
from symphony.bdk.core.auth.exception import AuthInitializationException


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
async def test_refresh_obo():
    mock_obo_authenticator = AsyncMock()
    mock_obo_authenticator.retrieve_obo_session_token_by_user_id.side_effect = ["session_token1", "session_token2"]
    mock_obo_authenticator.retrieve_obo_session_token_by_username.side_effect = ["session_token3", "session_token4"]

    obo_session = OboAuthSession(mock_obo_authenticator, user_id=1234)

    assert await obo_session.session_token == "session_token1"

    await obo_session.refresh()
    assert await obo_session.session_token == "session_token2"

    obo_session = OboAuthSession(mock_obo_authenticator, username="username")

    assert await obo_session.session_token == "session_token3"

    await obo_session.refresh()
    assert await obo_session.session_token == "session_token4"


def test_obo_init_failed():
    with pytest.raises(AuthInitializationException):
        OboAuthSession(None, user_id=1234, username="username")

    with pytest.raises(AuthInitializationException):
        OboAuthSession(None)
