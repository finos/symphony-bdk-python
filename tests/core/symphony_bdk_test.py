from unittest.mock import MagicMock

import pytest
from asyncmock import AsyncMock

from symphony.bdk.core.auth.authenticator_factory import AuthenticatorFactory
from symphony.bdk.core.auth.bot_authenticator import BotAuthenticatorRSA
from symphony.bdk.core.config.bdk_config_loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from tests.utils.resource_utils import get_config_resource_filepath


@pytest.fixture()
def config():
    return BdkConfigLoader.load_from_file(get_config_resource_filepath("config.yaml"))


@pytest.mark.asyncio
async def test_bot_session(config):
    authenticator_factory = MagicMock(AuthenticatorFactory)
    bot_authenticator = AsyncMock(BotAuthenticatorRSA)
    bot_authenticator.authenticate_bot.return_value = MockedAuthSession()
    authenticator_factory.get_bot_authenticator.return_value = bot_authenticator

    symphony_bdk = SymphonyBdk(config)
    symphony_bdk._authenticator_factory = authenticator_factory
    auth_session = await symphony_bdk.bot_session()
    assert auth_session is not None
    assert auth_session.session_token == 'session_token'
    assert auth_session.key_manager_token == 'km_token'


class MockedAuthSession:

    def __init__(self):
        self.session_token = "session_token"
        self.key_manager_token = "km_token"
