from asyncmock import AsyncMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession


@pytest.mark.asyncio
async def test_refresh():
    mock_bot_authenticator = AsyncMock()
    mock_bot_authenticator.retrieve_session_token.return_value = "session_token"
    mock_bot_authenticator.retrieve_key_manager_token.return_value = "km_token"

    auth_session = AuthSession(mock_bot_authenticator)
    await auth_session.refresh()
    assert auth_session.session_token == "session_token"
    assert auth_session.key_manager_token == "km_token"
