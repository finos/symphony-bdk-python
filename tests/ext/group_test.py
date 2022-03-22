from unittest.mock import Mock, AsyncMock, MagicMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.auth.bot_authenticator import BotAuthenticator
from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig
from symphony.bdk.core.service.user.user_util import extract_tenant_id
from symphony.bdk.ext.group import SymphonyGroupBdkExtension, SymphonyGroupService, OAuthSession
from symphony.bdk.gen import ApiClient, Configuration, ApiException
from symphony.bdk.gen.group_model.add_member import AddMember
from symphony.bdk.gen.group_model.create_group import CreateGroup
from symphony.bdk.gen.group_model.group_list import GroupList
from symphony.bdk.gen.group_model.member import Member
from symphony.bdk.gen.group_model.owner import Owner
from symphony.bdk.gen.group_model.read_group import ReadGroup
from symphony.bdk.gen.group_model.sort_order import SortOrder
from symphony.bdk.gen.group_model.status import Status
from symphony.bdk.gen.group_model.update_group import UpdateGroup
from symphony.bdk.gen.group_model.upload_avatar import UploadAvatar
from symphony.bdk.gen.login_api.authentication_api import AuthenticationApi
from symphony.bdk.gen.login_model.jwt_token import JwtToken

SESSION_TOKEN = "session_token"


@pytest.fixture(name="auth_session")
def fixture_auth_session():
    auth_session = AuthSession(None)
    auth_session.session_token = SESSION_TOKEN
    auth_session.key_manager_token = "km_token"
    return auth_session


@pytest.fixture(name="api_client_factory")
def fixture_api_client_factory(api_client, login_client):
    factory = AsyncMock(ApiClientFactory)
    factory.get_client.return_value = api_client
    factory.get_login_client.return_value = login_client
    return factory


@pytest.fixture(name="api_client")
def fixture_api_client():
    api_client = MagicMock(wraps=ApiClient())
    api_client.call_api = AsyncMock()
    api_client.configuration = Configuration()
    return api_client


@pytest.fixture(name="login_client")
def fixture_login_client():
    api_client = MagicMock(ApiClient)
    api_client.call_api = AsyncMock()
    api_client.configuration = Configuration()
    return api_client


@pytest.fixture(name="retry_config")
def fixture_retry_config():
    return BdkRetryConfig({"maxAttempts": 2, "multiplier": 1, "initialIntervalMillis": 50})


@pytest.fixture(name="group_service")
def fixture_group_service(api_client_factory, auth_session, retry_config):
    return SymphonyGroupService(api_client_factory, auth_session, retry_config)


@pytest.fixture(name="mocked_group")
def fixture_group():
    return ReadGroup(type="SDL", owner_type=Owner(value="TENANT"), owner_id=123, name="SDl test")


def assert_called_idm_tokens(first_call_args, session_token=SESSION_TOKEN):
    assert first_call_args.args[0] == "/idm/tokens"
    params = dict(first_call_args.args[3])
    assert params["scope"] == "profile-manager"
    assert first_call_args.args[4]["sessionToken"] == session_token


def test_group_extension_initialisation():
    api_client_factory = Mock()
    bot_session = Mock()
    config = Mock()
    extension = SymphonyGroupBdkExtension()
    extension.set_api_client_factory(api_client_factory)
    extension.set_bot_session(bot_session)
    extension.set_config(config)
    group_service = extension.get_service()

    assert isinstance(group_service, SymphonyGroupService)
    assert extension._api_client_factory == api_client_factory
    assert extension._bot_session == bot_session


@pytest.mark.asyncio
async def test_insert_group(group_service, mocked_group, api_client):
    api_client.call_api.return_value = mocked_group

    create_group = CreateGroup(type="SDL", owner_type=Owner(value="TENANT"), owner_id=190, name="SDL")
    group = await group_service.insert_group(create_group)

    assert group.type == mocked_group.type
    assert group.name == mocked_group.name
    api_client.call_api.assert_called_once()
    assert api_client.call_api.call_args.args[0] == "/v1/groups"
    assert api_client.call_api.call_args.kwargs["body"] == create_group


@pytest.mark.asyncio
async def test_list_groups(group_service, mocked_group, api_client):
    api_client.call_api.return_value = GroupList(data=[mocked_group])

    groups = await group_service.list_groups()
    assert len(groups.data) == 1
    api_client.call_api.assert_called_once()
    assert api_client.call_api.call_args.args[0] == "/v1/groups/type/{typeId}"


@pytest.mark.asyncio
async def test_list_groups_with_params(group_service, mocked_group, api_client):
    api_client.call_api.return_value = GroupList(data=[mocked_group])

    groups = await group_service.list_groups(status=Status(value="ACTIVE"), before="0", after="50", limit=50,
                                             sort_order=SortOrder(value="ASC"))
    assert len(groups.data) == 1
    api_client.call_api.assert_called_once()
    assert api_client.call_api.call_args.args[0] == "/v1/groups/type/{typeId}"
    params = dict(api_client.call_api.call_args.args[3])
    assert params["status"] == Status(value="ACTIVE")
    assert params["before"] == "0"
    assert params["after"] == "50"
    assert params["limit"] == 50
    assert params["sortOrder"] == SortOrder(value="ASC")


@pytest.mark.asyncio
async def test_update_group(group_service, mocked_group, api_client):
    mocked_group.name = "Updated name"
    mocked_group.e_tag = "e_tag"
    mocked_group.id = "group_id"
    api_client.call_api.return_value = mocked_group

    update_group = UpdateGroup(name="Updated name", type=mocked_group.type, owner_type=Owner(value="TENANT"),
                               owner_id=mocked_group.owner_id, id=mocked_group.id, e_tag=mocked_group.e_tag,
                               status=Status(value="ACTIVE"))
    group = await group_service.update_group(if_match=mocked_group.e_tag, group_id=mocked_group.id,
                                             update_group=update_group)

    assert group.name == mocked_group.name
    api_client.call_api.assert_called_once()
    assert api_client.call_api.call_args.args[0] == "/v1/groups/{groupId}"
    assert api_client.call_api.call_args.kwargs["body"] == update_group


@pytest.mark.asyncio
async def test_update_avatar(group_service, mocked_group, api_client):
    mocked_group.id = "group_id"
    api_client.call_api.return_value = mocked_group

    image = "base_64_image"
    group = await group_service.update_avatar(group_id=mocked_group.id, image=image)

    assert group.name == mocked_group.name
    api_client.call_api.assert_called_once()
    assert api_client.call_api.call_args.args[0] == "/v1/groups/{groupId}/avatar"
    assert api_client.call_api.call_args.kwargs["body"] == UploadAvatar(image=image)


@pytest.mark.asyncio
async def test_get_group(group_service, mocked_group, api_client):
    mocked_group.id = "group_id"
    api_client.call_api.return_value = mocked_group

    group = await group_service.get_group(group_id=mocked_group.id)

    assert group.name == mocked_group.name
    api_client.call_api.assert_called_once()
    assert api_client.call_api.call_args.args[0] == "/v1/groups/{groupId}"


@pytest.mark.asyncio
async def test_add_member_to_group(group_service, mocked_group, api_client):
    mocked_group.id = "group_id"
    api_client.call_api.return_value = mocked_group
    user_id = 12345
    group = await group_service.add_member_to_group(group_id=mocked_group.id, user_id=user_id)

    assert group.name == mocked_group.name
    api_client.call_api.assert_called_once()
    assert api_client.call_api.call_args.args[0] == "/v1/groups/{groupId}/member"
    assert api_client.call_api.call_args.kwargs["body"] == AddMember(member=Member(
        member_id=user_id, member_tenant=extract_tenant_id(user_id)))


@pytest.mark.asyncio
async def test_add_member_to_group_with_retries(group_service, mocked_group, api_client, login_client):
    login_client.call_api.return_value = JwtToken(access_token="access token")

    mocked_group.id = "group_id"
    api_client.call_api.side_effect = [ApiException(status=401), mocked_group]
    user_id = 12345

    group = await group_service.add_member_to_group(group_id=mocked_group.id, user_id=user_id)

    login_client.call_api.assert_called_once()
    assert group.name == mocked_group.name
    assert api_client.call_api.call_count == 2
    assert api_client.call_api.call_args.args[0] == "/v1/groups/{groupId}/member"
    assert api_client.call_api.call_args.kwargs["body"] == AddMember(member=Member(
        member_id=user_id, member_tenant=extract_tenant_id(user_id)))


@pytest.mark.asyncio
async def test_oauth_session_initialisation(auth_session, retry_config):
    oauth_session = OAuthSession(AsyncMock(), auth_session, retry_config)

    assert isinstance(oauth_session._authentication_api, AuthenticationApi)
    assert oauth_session._bearer_token is None
    assert oauth_session._session == auth_session
    assert oauth_session._retry_config == retry_config


@pytest.mark.asyncio
async def test_oauth_session_refresh(auth_session, retry_config, login_client):
    bearer_token = "bearer token"
    token = JwtToken(access_token=bearer_token)
    login_client.call_api.return_value = token

    oauth_session = OAuthSession(login_client, auth_session, retry_config)
    await oauth_session.refresh()

    login_client.call_api.assert_called_once()
    assert_called_idm_tokens(login_client.call_api.call_args)
    assert oauth_session._bearer_token == bearer_token


@pytest.mark.asyncio
async def test_oauth_session_refresh_with_retries(auth_session, retry_config, login_client):
    bearer_token = "bearer token"
    login_client.call_api.side_effect = [ApiException(status=401), JwtToken(access_token=bearer_token)]
    authenticator = AsyncMock(BotAuthenticator)
    auth_session._authenticator = authenticator
    updated_session_token = "updated session token"
    authenticator.retrieve_session_token.return_value = updated_session_token

    oauth_session = OAuthSession(login_client, auth_session, retry_config)
    await oauth_session.refresh()

    assert login_client.call_api.call_count == 2
    assert_called_idm_tokens(login_client.call_api.call_args_list[0])
    assert_called_idm_tokens(login_client.call_api.call_args_list[1], updated_session_token)
    assert oauth_session._bearer_token == bearer_token


@pytest.mark.asyncio
async def test_oauth_settings(auth_session, retry_config, login_client):
    bearer_token = "bearer token"
    token = JwtToken(access_token=bearer_token)
    login_client.call_api.return_value = token

    oauth_session = OAuthSession(login_client, auth_session, retry_config)
    settings = await oauth_session.get_auth_settings()

    assert settings == {"bearerAuth": {"in": "header",
                                       "key": "Authorization",
                                       "type": "bearer",
                                       "value": "Bearer bearer token"}}
    login_client.call_api.assert_called_once()


@pytest.mark.asyncio
async def test_oauth_settings_does_not_refresh_when_called_twice(auth_session, retry_config, login_client):
    bearer_token = "bearer token"
    token = JwtToken(access_token=bearer_token)
    login_client.call_api.return_value = token

    oauth_session = OAuthSession(login_client, auth_session, retry_config)
    await oauth_session.get_auth_settings()
    settings = await oauth_session.get_auth_settings()

    assert settings == {"bearerAuth": {"in": "header",
                                       "key": "Authorization",
                                       "type": "bearer",
                                       "value": "Bearer bearer token"}}
    login_client.call_api.assert_called_once()
