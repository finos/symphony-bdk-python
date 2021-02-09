from unittest.mock import patch

import pytest
from unittest.mock import AsyncMock

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.auth.bot_authenticator import BotAuthenticatorRsa
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from tests.utils.resource_utils import get_config_resource_filepath


@pytest.fixture()
def config():
    return BdkConfigLoader.load_from_file(get_config_resource_filepath("config.yaml"))


@pytest.mark.asyncio
async def test_bot_session(config):
    with patch('symphony.bdk.core.auth.bot_authenticator.create_signed_jwt', return_value='privateKey'):
        bot_authenticator = AsyncMock(BotAuthenticatorRsa)
        bot_authenticator.retrieve_session_token.return_value = "session_token"
        bot_authenticator.retrieve_key_manager_token.return_value = "km_token"
        bot_session = AuthSession(bot_authenticator)
        async with SymphonyBdk(config) as symphony_bdk:
            symphony_bdk._bot_session = bot_session
            auth_session = symphony_bdk.bot_session()
            assert auth_session is not None
            assert await auth_session.session_token == 'session_token'
            assert await auth_session.key_manager_token == 'km_token'
