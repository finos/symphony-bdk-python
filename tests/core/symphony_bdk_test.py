from unittest.mock import AsyncMock, Mock
from unittest.mock import patch

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession, OboAuthSession
from symphony.bdk.core.auth.bot_authenticator import BotAuthenticatorRsa
from symphony.bdk.core.auth.exception import AuthInitializationError
from symphony.bdk.core.auth.obo_authenticator import OboAuthenticatorRsa
from symphony.bdk.core.config.exception import BotNotConfiguredError, BdkConfigError
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from tests.utils.resource_utils import get_config_resource_filepath


@pytest.fixture(name="config")
def fixture_config():
    return BdkConfigLoader.load_from_file(get_config_resource_filepath("config.yaml"))


@pytest.fixture(name="invalid_username_config")
def fixture_invalid_username_config():
    return BdkConfig(host="acme.symphony.com", bot={"privateKey": {"path": "/path/to/key.pem"}})


@pytest.fixture(name="invalid_app_id_config")
def fixture_invalid_app_id_config():
    return BdkConfig(host="acme.symphony.com", app={"privateKey": {"path": "/path/to/key.pem"}})


@pytest.fixture(name="obo_only_config")
def fixture_obo_only_config():
    return BdkConfig(host="acme.symphony.com", app={"appId": "app", "privateKey": {"path": "/path/to/key.pem"}})


@pytest.fixture(name="mock_obo_session")
def fixture_mock_obo_session():
    obo_session = AsyncMock(OboAuthSession)
    obo_session.session_token.return_value = "session_token"
    obo_session.key_manager_token.return_value = ""
    return obo_session


@pytest.mark.asyncio
async def test_bot_session(config):
    with patch("symphony.bdk.core.auth.bot_authenticator.create_signed_jwt", return_value="privateKey"):
        bot_authenticator = AsyncMock(BotAuthenticatorRsa)
        bot_authenticator.retrieve_session_token.return_value = "session_token"
        bot_authenticator.retrieve_key_manager_token.return_value = "km_token"
        bot_session = AuthSession(bot_authenticator)
        async with SymphonyBdk(config) as symphony_bdk:
            symphony_bdk._bot_session = bot_session
            auth_session = symphony_bdk.bot_session()
            assert auth_session is not None
            assert await auth_session.session_token == "session_token"
            assert await auth_session.key_manager_token == "km_token"


@pytest.mark.asyncio
async def test_bot_invalid_config_session(invalid_username_config):
    async with SymphonyBdk(invalid_username_config) as symphony_bdk:
        with pytest.raises(BotNotConfiguredError):
            symphony_bdk.bot_session()

        with pytest.raises(BotNotConfiguredError):
            symphony_bdk.messages()

        with pytest.raises(BotNotConfiguredError):
            symphony_bdk.streams()

        with pytest.raises(BotNotConfiguredError):
            symphony_bdk.datafeed()

        with pytest.raises(BotNotConfiguredError):
            symphony_bdk.users()

        with pytest.raises(BotNotConfiguredError):
            symphony_bdk.connections()


@pytest.mark.asyncio
async def test_obo_with_user_id(config):
    with patch.object(OboAuthenticatorRsa, "authenticate_by_user_id") as mock_authenticate:
        mock_authenticate.return_value = Mock(OboAuthSession)
        user_id = 12345

        async with SymphonyBdk(config) as symphony_bdk:
            obo_session = symphony_bdk.obo(user_id=user_id)

            assert obo_session is not None
            mock_authenticate.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_obo_with_username(config):
    with patch.object(OboAuthenticatorRsa, "authenticate_by_username") as mock_authenticate:
        mock_authenticate.return_value = Mock(OboAuthSession)
        username = "my.bot.user"

        async with SymphonyBdk(config) as symphony_bdk:
            obo_session = symphony_bdk.obo(username=username)

            assert obo_session is not None
            mock_authenticate.assert_called_once_with(username)


@pytest.mark.asyncio
async def test_obo_with_user_id_and_username(config):
    with patch.object(OboAuthenticatorRsa, "authenticate_by_username") as authenticate_by_username, \
            patch.object(OboAuthenticatorRsa, "authenticate_by_user_id") as authenticate_by_user_id:
        authenticate_by_user_id.return_value = Mock(OboAuthSession)
        user_id = 12345

        async with SymphonyBdk(config) as symphony_bdk:
            obo_session = symphony_bdk.obo(user_id=user_id, username="bot.user")

            assert obo_session is not None
            authenticate_by_user_id.assert_called_once_with(user_id)
            authenticate_by_username.assert_not_called()


@pytest.mark.asyncio
async def test_obo_services_with_app_only_config(obo_only_config, mock_obo_session):
    async with SymphonyBdk(obo_only_config) as symphony_bdk:
        async with symphony_bdk.obo_services(mock_obo_session) as obo_services:
            assert obo_services is not None


@pytest.mark.asyncio
async def test_obo_services(config, mock_obo_session):
    async with SymphonyBdk(config) as symphony_bdk:
        async with symphony_bdk.obo_services(mock_obo_session) as obo_services:
            assert obo_services is not None


@pytest.mark.asyncio
async def test_obo_fails(config):
    with pytest.raises(AuthInitializationError):
        async with SymphonyBdk(config) as symphony_bdk:
            symphony_bdk.obo()


@pytest.mark.asyncio
async def test_non_obo_services_fail_with_obo_only(obo_only_config):
    async with SymphonyBdk(obo_only_config) as symphony_bdk:
        with pytest.raises(BotNotConfiguredError):
            symphony_bdk.bot_session()

        with pytest.raises(BotNotConfiguredError):
            symphony_bdk.messages()

        with pytest.raises(BotNotConfiguredError):
            symphony_bdk.streams()

        with pytest.raises(BotNotConfiguredError):
            symphony_bdk.datafeed()

        with pytest.raises(BotNotConfiguredError):
            symphony_bdk.users()

        with pytest.raises(BotNotConfiguredError):
            symphony_bdk.connections()


@pytest.mark.asyncio
async def test_ext_app_authenticator(obo_only_config):
    async with SymphonyBdk(obo_only_config) as symphony_bdk:
        authenticator = symphony_bdk.app_authenticator()
        assert authenticator is not None
        assert symphony_bdk.app_authenticator() == authenticator  # test same instance is always returned


@pytest.mark.asyncio
async def test_invalid_app_config(invalid_app_id_config, mock_obo_session):
    async with SymphonyBdk(invalid_app_id_config) as symphony_bdk:
        with pytest.raises(BdkConfigError):
            symphony_bdk.app_authenticator()
        with pytest.raises(BdkConfigError):
            symphony_bdk.obo(username="username")
        with pytest.raises(BdkConfigError):
            symphony_bdk.obo(user_id=1234)
        with pytest.raises(BdkConfigError):
            symphony_bdk.obo_services(mock_obo_session)
