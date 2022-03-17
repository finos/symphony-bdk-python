from unittest.mock import Mock, AsyncMock, MagicMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.service.user.user_util import extract_tenant_id
from symphony.bdk.ext.group import SymphonyGroupBdkExtension, SymphonyGroupService
from symphony.bdk.gen import ApiClient, Configuration
from symphony.bdk.gen.group_model.add_member import AddMember
from symphony.bdk.gen.group_model.create_group import CreateGroup
from symphony.bdk.gen.group_model.group_list import GroupList
from symphony.bdk.gen.group_model.member import Member
from symphony.bdk.gen.group_model.owner import Owner
from symphony.bdk.gen.group_model.read_group import ReadGroup
from symphony.bdk.gen.group_model.status import Status
from symphony.bdk.gen.group_model.update_group import UpdateGroup
from symphony.bdk.gen.group_model.upload_avatar import UploadAvatar


@pytest.fixture(name="auth_session")
def fixture_auth_session():
    auth_session = AuthSession(None)
    auth_session.session_token = "session_token"
    auth_session.key_manager_token = "km_token"
    return auth_session


@pytest.fixture(name="api_client_factory")
def fixture_api_client_factory(api_client):
    factory = AsyncMock(ApiClientFactory)
    factory.get_client.return_value = api_client
    return factory

@pytest.fixture(name="api_client")
def fixture_mocked_api_client():
    api_client = MagicMock(ApiClient)
    api_client.call_api = AsyncMock()
    api_client.configuration = Configuration()
    return api_client

@pytest.fixture(name="group_service")
def fixture_group_service(api_client_factory, auth_session):
    return SymphonyGroupService(api_client_factory, auth_session)


@pytest.fixture(name="mocked_group")
def fixture_group():
    return ReadGroup(type="SDL", owner_type=Owner(value="TENANT"), owner_id=123, name="SDl test")


def test_group_extension_initialisation():
    api_client_factory = Mock()
    bot_session = Mock()
    extension = SymphonyGroupBdkExtension()
    extension.set_api_client_factory(api_client_factory)
    extension.set_bot_session(bot_session)
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
    assert api_client.call_api.call_args.kwargs["body"] == AddMember(member= Member(
        member_id=user_id, member_tenant=extract_tenant_id(user_id)))
