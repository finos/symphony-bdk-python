from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.auth.bot_authenticator import BotAuthenticator
from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig
from symphony.bdk.core.service.user.user_util import extract_tenant_id
from symphony.bdk.ext.group import OAuthSession, SymphonyGroupBdkExtension, SymphonyGroupService
from symphony.bdk.gen import ApiClient, ApiException, Configuration
from symphony.bdk.gen.group_model.add_member import AddMember
from symphony.bdk.gen.group_model.create_group import CreateGroup
from symphony.bdk.gen.group_model.group_list import GroupList
from symphony.bdk.gen.group_model.member import Member
from symphony.bdk.gen.group_model.owner import Owner
from symphony.bdk.gen.group_api.group_api import GroupApi
from symphony.bdk.gen.group_model.read_group import ReadGroup
from symphony.bdk.gen.group_model.sort_order import SortOrder
from symphony.bdk.gen.group_model.status import Status
from symphony.bdk.gen.group_model.update_group import UpdateGroup
from symphony.bdk.gen.group_model.upload_avatar import UploadAvatar
from symphony.bdk.gen.login_api.authentication_api import AuthenticationApi
from symphony.bdk.gen.login_model.jwt_token import JwtToken
from tests.utils.resource_utils import get_deserialized_object_from_resource

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
    api_client = MagicMock(ApiClient)
    api_client.call_api = AsyncMock()
    api_client.configuration = Configuration()
    return api_client


@pytest.fixture(name="login_client")
def fixture_login_client():
    login_client = MagicMock(ApiClient)
    login_client.call_api = AsyncMock()
    login_client.configuration = Configuration()
    return login_client


@pytest.fixture(name="retry_config")
def fixture_retry_config():
    return BdkRetryConfig({"maxAttempts": 2, "multiplier": 1, "initialIntervalMillis": 50})


@pytest.fixture(name="group_service")
def fixture_group_service(api_client_factory, auth_session, retry_config):
    return SymphonyGroupService(api_client_factory, auth_session, retry_config)


@pytest.fixture(name="mocked_group")
def fixture_group():
    return ReadGroup(type="SDL", owner_type=Owner(value="TENANT"), owner_id=123, name="SDl test")


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
async def test_insert_group(group_service, mocked_group):
    group_api = MagicMock(spec=GroupApi)
    group_api.insert_group = AsyncMock(return_value=mocked_group)
    group_service._group_api = group_api

    create_group = CreateGroup(
        type="SDL", owner_type=Owner(value="TENANT"), owner_id=190, name="SDL"
    )
    group = await group_service.insert_group(create_group)

    assert group.type == mocked_group.type
    assert group.name == mocked_group.name
    group_api.insert_group.assert_called_once()
    call_kwargs = group_api.insert_group.call_args.kwargs
    assert call_kwargs["create_group"] == create_group
    assert call_kwargs["x_symphony_host"] == "localhost"


@pytest.mark.asyncio
async def test_list_groups(group_service, mocked_group):
    group_api = MagicMock(spec=GroupApi)
    group_api.list_groups = AsyncMock(return_value=GroupList(data=[mocked_group]))
    group_service._group_api = group_api

    groups = await group_service.list_groups()
    assert len(groups.data) == 1
    group_api.list_groups.assert_called_once()
    call_kwargs = group_api.list_groups.call_args.kwargs
    assert call_kwargs["x_symphony_host"] == "localhost"


@pytest.mark.asyncio
async def test_list_all_groups(group_service):
    group_api = MagicMock(spec=GroupApi)
    group_api.list_groups = AsyncMock(return_value=get_deserialized_object_from_resource(
        GroupList, "group/list_all_groups_one_page.json"
    ))
    group_service._group_api = group_api

    gen = await group_service.list_all_groups(chunk_size=2)
    groups = [d async for d in gen]

    group_api.list_groups.assert_called_once()
    call_kwargs = group_api.list_groups.call_args.kwargs
    assert call_kwargs["limit"] == 2
    assert len(groups) == 2
    assert groups[0].name == "SDl test 0"
    assert groups[1].name == "SDl test 1"


@pytest.mark.asyncio
async def test_list_all_groups_2_pages(group_service):
    return_values = [
        get_deserialized_object_from_resource(GroupList, "group/list_all_groups_page_1.json"),
        get_deserialized_object_from_resource(GroupList, "group/list_all_groups_page_2.json"),
    ]
    group_api = MagicMock(spec=GroupApi)
    group_api.list_groups = AsyncMock(side_effect=return_values)
    group_service._group_api = group_api

    gen = await group_service.list_all_groups(chunk_size=2, max_number=4)
    groups = [d async for d in gen]

    assert group_api.list_groups.call_count == 2
    call_kwargs = group_api.list_groups.call_args.kwargs
    assert call_kwargs["after"] == "2"
    assert call_kwargs["limit"] == 2
    assert len(groups) == 4
    assert groups[0].name == "SDl test 0"
    assert groups[1].name == "SDl test 1"
    assert groups[2].name == "SDl test 2"
    assert groups[3].name == "SDl test 3"


@pytest.mark.asyncio
async def test_list_groups_with_params(group_service, mocked_group):
    group_api = MagicMock(spec=GroupApi)
    group_api.list_groups = AsyncMock(return_value=GroupList(data=[mocked_group]))
    group_service._group_api = group_api

    groups = await group_service.list_groups(
        status=Status(value="ACTIVE"),
        before="0",
        after="50",
        limit=50,
        sort_order=SortOrder(value="ASC"),
    )
    assert len(groups.data) == 1
    group_api.list_groups.assert_called_once()
    call_kwargs = group_api.list_groups.call_args.kwargs
    assert call_kwargs["status"] == Status(value="ACTIVE")
    assert call_kwargs["before"] == "0"
    assert call_kwargs["after"] == "50"
    assert call_kwargs["limit"] == 50
    assert call_kwargs["sort_order"] == SortOrder(value="ASC")


@pytest.mark.asyncio
async def test_update_group(group_service, mocked_group):
    mocked_group.name = "Updated name"
    mocked_group.e_tag = "e_tag"
    mocked_group.id = "group_id"
    group_api = MagicMock(spec=GroupApi)
    group_api.update_group = AsyncMock(return_value=mocked_group)
    group_service._group_api = group_api

    update_group = UpdateGroup(
        name="Updated name",
        type=mocked_group.type,
        owner_type=Owner(value="TENANT"),
        owner_id=mocked_group.owner_id,
        id=mocked_group.id,
        e_tag=mocked_group.e_tag,
        status=Status(value="ACTIVE"),
    )
    group = await group_service.update_group(
        if_match=mocked_group.e_tag, group_id=mocked_group.id, update_group=update_group
    )

    assert group.name == mocked_group.name
    group_api.update_group.assert_called_once()
    call_kwargs = group_api.update_group.call_args.kwargs
    assert call_kwargs["if_match"] == mocked_group.e_tag
    assert call_kwargs["group_id"] == mocked_group.id
    assert call_kwargs["update_group"] == update_group


@pytest.mark.asyncio
async def test_update_avatar(group_service, mocked_group):
    mocked_group.id = "group_id"
    group_api = MagicMock(spec=GroupApi)
    group_api.update_avatar = AsyncMock(return_value=mocked_group)
    group_service._group_api = group_api

    image = "base_64_image"
    group = await group_service.update_avatar(group_id=mocked_group.id, image=image)

    assert group.name == mocked_group.name
    group_api.update_avatar.assert_called_once()
    call_kwargs = group_api.update_avatar.call_args.kwargs
    assert call_kwargs["group_id"] == mocked_group.id
    assert call_kwargs["upload_avatar"] == UploadAvatar(image=image)


@pytest.mark.asyncio
async def test_get_group(group_service, mocked_group):
    mocked_group.id = "group_id"
    group_api = MagicMock(spec=GroupApi)
    group_api.get_group = AsyncMock(return_value=mocked_group)
    group_service._group_api = group_api

    group = await group_service.get_group(group_id=mocked_group.id)

    assert group.name == mocked_group.name
    group_api.get_group.assert_called_once_with(group_id=mocked_group.id, x_symphony_host="localhost")


@pytest.mark.asyncio
async def test_add_member_to_group(group_service, mocked_group):
    mocked_group.id = "group_id"
    group_api = MagicMock(spec=GroupApi)
    group_api.add_member_to_group = AsyncMock(return_value=mocked_group)
    group_service._group_api = group_api
    user_id = 12345
    group = await group_service.add_member_to_group(group_id=mocked_group.id, user_id=user_id)

    assert group.name == mocked_group.name
    group_api.add_member_to_group.assert_called_once()
    call_kwargs = group_api.add_member_to_group.call_args.kwargs
    assert call_kwargs["group_id"] == mocked_group.id
    assert call_kwargs["add_member"] == AddMember(
        member=Member(member_id=user_id, member_tenant=extract_tenant_id(user_id))
    )


@pytest.mark.asyncio
async def test_add_member_to_group_with_retries(
    group_service, mocked_group
):
    authentication_api = group_service._oauth_session._authentication_api
    authentication_api.idm_tokens_post = AsyncMock(return_value=JwtToken(access_token="access token"))
    
    mocked_group.id = "group_id"
    group_api = MagicMock(spec=GroupApi)
    group_api.add_member_to_group = AsyncMock(side_effect=[ApiException(status=401), mocked_group])
    group_service._group_api = group_api
    user_id = 12345

    group = await group_service.add_member_to_group(group_id=mocked_group.id, user_id=user_id)

    authentication_api.idm_tokens_post.assert_called_once()
    assert group.name == mocked_group.name
    assert group_api.add_member_to_group.call_count == 2
    call_kwargs = group_api.add_member_to_group.call_args.kwargs
    assert call_kwargs["group_id"] == mocked_group.id
    assert call_kwargs["add_member"] == AddMember(
        member=Member(member_id=user_id, member_tenant=extract_tenant_id(user_id))
    )


@pytest.mark.asyncio
async def test_oauth_session_initialisation(auth_session, retry_config):
    oauth_session = OAuthSession(AsyncMock(), auth_session, retry_config)

    assert isinstance(oauth_session._authentication_api, AuthenticationApi)
    assert oauth_session._bearer_token is None
    assert oauth_session._auth_session == auth_session
    assert oauth_session._retry_config == retry_config


@pytest.mark.asyncio
async def test_oauth_session_refresh(auth_session, retry_config):
    bearer_token = "bearer token"
    token = JwtToken(access_token=bearer_token)

    oauth_session = OAuthSession(AsyncMock(), auth_session, retry_config)
    oauth_session._authentication_api.idm_tokens_post = AsyncMock(return_value=token)
    await oauth_session.refresh()

    oauth_session._authentication_api.idm_tokens_post.assert_called_once_with(
        session_token=SESSION_TOKEN, scope="profile-manager"
    )
    assert oauth_session._bearer_token == bearer_token


@pytest.mark.asyncio
async def test_oauth_session_refresh_with_retries(auth_session, retry_config):
    bearer_token = "bearer token"
    oauth_session = OAuthSession(AsyncMock(), auth_session, retry_config)
    oauth_session._authentication_api.idm_tokens_post = AsyncMock(side_effect=[
        ApiException(status=401),
        JwtToken(access_token=bearer_token),
    ])
    authenticator = AsyncMock(BotAuthenticator)
    auth_session._authenticator = authenticator
    updated_session_token = "updated session token"
    authenticator.retrieve_session_token.return_value = updated_session_token

    await oauth_session.refresh()

    assert oauth_session._authentication_api.idm_tokens_post.call_count == 2
    first_call_kwargs = oauth_session._authentication_api.idm_tokens_post.call_args_list[0].kwargs
    assert first_call_kwargs["session_token"] == SESSION_TOKEN
    second_call_kwargs = oauth_session._authentication_api.idm_tokens_post.call_args_list[1].kwargs
    assert second_call_kwargs["session_token"] == updated_session_token
    assert oauth_session._bearer_token == bearer_token


@pytest.mark.asyncio
async def test_oauth_settings(auth_session, retry_config):
    bearer_token = "bearer token"
    token = JwtToken(access_token=bearer_token)

    oauth_session = OAuthSession(AsyncMock(), auth_session, retry_config)
    oauth_session._authentication_api.idm_tokens_post = AsyncMock(return_value=token)
    settings = await oauth_session.get_auth_settings()

    assert settings == {
        "bearerAuth": {
            "in": "header",
            "key": "Authorization",
            "type": "bearer",
            "value": "Bearer bearer token",
        }
    }
    oauth_session._authentication_api.idm_tokens_post.assert_called_once()


@pytest.mark.asyncio
async def test_oauth_settings_does_not_refresh_when_called_twice(
    auth_session, retry_config
):
    bearer_token = "bearer token"
    token = JwtToken(access_token=bearer_token)

    oauth_session = OAuthSession(AsyncMock(), auth_session, retry_config)
    oauth_session._authentication_api.idm_tokens_post = AsyncMock(return_value=token)
    await oauth_session.get_auth_settings()
    settings = await oauth_session.get_auth_settings()

    assert settings == {
        "bearerAuth": {
            "in": "header",
            "key": "Authorization",
            "type": "bearer",
            "value": "Bearer bearer token",
        }
    }
    oauth_session._authentication_api.idm_tokens_post.assert_called_once()
