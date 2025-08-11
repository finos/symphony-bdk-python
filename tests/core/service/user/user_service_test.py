import base64
import json
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.user.model.delegate_action_enum import DelegateActionEnum
from symphony.bdk.core.service.user.model.role_id import RoleId
from symphony.bdk.core.service.user.user_service import UserService
from symphony.bdk.gen.agent_api.audit_trail_api import AuditTrailApi
from symphony.bdk.gen.agent_model.v1_audit_trail_initiator_list import (
    V1AuditTrailInitiatorList,
)
from symphony.bdk.gen.pod_api.system_api import SystemApi
from symphony.bdk.gen.pod_api.user_api import UserApi
from symphony.bdk.gen.pod_api.users_api import UsersApi
from symphony.bdk.gen.pod_model.avatar_list import AvatarList
from symphony.bdk.gen.pod_model.avatar_update import AvatarUpdate
from symphony.bdk.gen.pod_model.delegate_action import DelegateAction
from symphony.bdk.gen.pod_model.disclaimer import Disclaimer
from symphony.bdk.gen.pod_model.feature import Feature
from symphony.bdk.gen.pod_model.feature_list import FeatureList
from symphony.bdk.gen.pod_model.followers_list import FollowersList
from symphony.bdk.gen.pod_model.followers_list_response import FollowersListResponse
from symphony.bdk.gen.pod_model.following_list_response import FollowingListResponse
from symphony.bdk.gen.pod_model.integer_list import IntegerList
from symphony.bdk.gen.pod_model.role_detail_list import RoleDetailList
from symphony.bdk.gen.pod_model.service_account_manifest import ServiceAccountManifest
from symphony.bdk.gen.pod_model.string_id import StringId
from symphony.bdk.gen.pod_model.user_detail_list import UserDetailList
from symphony.bdk.gen.pod_model.user_filter import UserFilter
from symphony.bdk.gen.pod_model.user_id_list import UserIdList
from symphony.bdk.gen.pod_model.user_search_filter import UserSearchFilter
from symphony.bdk.gen.pod_model.user_search_query import UserSearchQuery
from symphony.bdk.gen.pod_model.user_search_results import UserSearchResults
from symphony.bdk.gen.pod_model.user_status import UserStatus
from symphony.bdk.gen.pod_model.user_suspension import UserSuspension
from symphony.bdk.gen.pod_model.v2_user_attributes import V2UserAttributes
from symphony.bdk.gen.pod_model.v2_user_create import V2UserCreate
from symphony.bdk.gen.pod_model.v2_user_detail import V2UserDetail
from symphony.bdk.gen.pod_model.v2_user_detail_list import V2UserDetailList
from symphony.bdk.gen.pod_model.v2_user_list import V2UserList
from tests.core.config import minimal_retry_config
from tests.utils.resource_utils import (
    deserialize_object,
    get_deserialized_object_from_resource,
    get_resource_filepath,
)


@pytest.fixture(name="auth_session")
def fixture_auth_session():
    auth_session = AuthSession(None)
    auth_session.session_token = "session_token"
    auth_session.key_manager_token = "km_token"
    return auth_session


@pytest.fixture(name="user_api")
def fixture_user_api():
    return MagicMock(UserApi)


@pytest.fixture(name="users_api")
def fixture_users_api():
    return MagicMock(UsersApi)


@pytest.fixture(name="audit_trail_api")
def fixture_audit_trail_api():
    return MagicMock(AuditTrailApi)


@pytest.fixture(name="system_api")
def fixture_system_api():
    return MagicMock(SystemApi)


@pytest.fixture(name="user_service")
def fixture_user_service(
    user_api, users_api, audit_trail_api, system_api, auth_session
):
    service = UserService(
        user_api,
        users_api,
        audit_trail_api,
        system_api,
        auth_session,
        minimal_retry_config(),
        "manifest.json",
    )
    return service


@pytest.mark.asyncio
async def test_list_users_by_ids(users_api, user_service):
    users_api.v3_users_get = AsyncMock()
    users_api.v3_users_get.return_value = get_deserialized_object_from_resource(
        V2UserList, "user/list_user.json"
    )
    users_list = await user_service.list_users_by_ids(
        [15942919536460, 15942919536461], active=True
    )

    users_api.v3_users_get.assert_called_with(
        uid="15942919536460,15942919536461",
        local=False,
        session_token="session_token",
        active=True,
    )
    assert len(users_list.users) == 2
    assert len(users_list.errors) == 2
    assert users_list.users[0].username == "tw"


@pytest.mark.asyncio
async def test_list_users_by_emails(users_api, user_service):
    users_api.v3_users_get = AsyncMock()
    users_api.v3_users_get.return_value = get_deserialized_object_from_resource(
        V2UserList, "user/list_user.json"
    )
    users_list = await user_service.list_users_by_emails(
        ["technicalwriter@symphony.com", "serviceaccount@symphony.com"], active=True
    )

    users_api.v3_users_get.assert_called_with(
        email="technicalwriter@symphony.com,serviceaccount@symphony.com",
        local=False,
        session_token="session_token",
        active=True,
    )
    assert len(users_list.users) == 2
    assert len(users_list.errors) == 2
    assert users_list.users[0].username == "tw"


@pytest.mark.asyncio
async def test_list_users_by_usernames(users_api, user_service):
    users_api.v3_users_get = AsyncMock()
    users_api.v3_users_get.return_value = get_deserialized_object_from_resource(
        V2UserList, "user/list_user.json"
    )
    users_list = await user_service.list_users_by_usernames(["tw", "SA"], active=True)

    users_api.v3_users_get.assert_called_with(
        username="tw,SA", local=True, session_token="session_token", active=True
    )

    assert len(users_list.users) == 2
    assert len(users_list.errors) == 2
    assert users_list.users[0].email_address == "technicalwriter@symphony.com"


@pytest.mark.asyncio
async def test_search_users(users_api, user_service):
    users_api.v1_user_search_post = AsyncMock()
    users_api.v1_user_search_post.return_value = get_deserialized_object_from_resource(
        UserSearchResults, "user/search_user.json"
    )
    query = UserSearchQuery(
        query="jane",
        filters=UserSearchFilter(title="Sales Manager", company="Symphony"),
    )

    result = await user_service.search_users(query)

    users_api.v1_user_search_post.assert_called_with(
        search_request=query,
        local=False,
        skip=0,
        limit=50,
        session_token="session_token",
    )
    assert result.count == 1
    assert len(result.users) == 1
    assert result.users[0].id == 13056700581099


@pytest.mark.asyncio
async def test_search_all_users(users_api, user_service):
    users_api.v1_user_search_post = AsyncMock()
    users_api.v1_user_search_post.return_value = get_deserialized_object_from_resource(
        UserSearchResults, "user/search_user.json"
    )
    query = UserSearchQuery(
        query="jane",
        filters=UserSearchFilter(title="Sales Manager", company="Symphony"),
    )

    gen = await user_service.search_all_users(query)
    result = [u async for u in gen]

    users_api.v1_user_search_post.assert_called_with(
        search_request=query,
        local=False,
        skip=0,
        limit=50,
        session_token="session_token",
    )
    assert len(result) == 1
    assert result[0].id == 13056700581099


@pytest.mark.asyncio
async def test_follow_user(user_api, user_service):
    user_api.v1_user_uid_follow_post = AsyncMock()

    await user_service.follow_user([1234, 2345], 12345)

    user_api.v1_user_uid_follow_post.assert_called_with(
        uid=12345,
        uid_list=FollowersList(followers=UserIdList(value=[1234, 2345])),
        session_token="session_token",
    )


@pytest.mark.asyncio
async def test_unfollow_user(user_api, user_service):
    user_api.v1_user_uid_unfollow_post = AsyncMock()

    await user_service.unfollow_user([1234, 2345], 12345)

    user_api.v1_user_uid_unfollow_post.assert_called_with(
        uid=12345,
        uid_list=FollowersList(followers=UserIdList(value=[1234, 2345])),
        session_token="session_token",
    )


@pytest.mark.asyncio
async def test_get_user_detail(user_api, user_service):
    user_api.v2_admin_user_uid_get = AsyncMock()
    user_api.v2_admin_user_uid_get.return_value = get_deserialized_object_from_resource(
        V2UserDetail, "user/user_detail.json"
    )

    user_detail = await user_service.get_user_detail(7215545078461)

    user_api.v2_admin_user_uid_get.assert_called_with(
        uid=7215545078461, session_token="session_token"
    )

    assert user_detail.user_attributes.user_name == "johndoe"
    assert user_detail.user_system_info.status == "ENABLED"
    assert len(user_detail.roles.value) == 6


@pytest.mark.asyncio
async def test_list_user_details(user_api, user_service):
    user_api.v2_admin_user_list_get = AsyncMock()
    user_api.v2_admin_user_list_get.return_value = (
        get_deserialized_object_from_resource(
            V2UserDetailList, "user/list_user_detail.json"
        )
    )

    user_detail_list = await user_service.list_user_details()

    user_api.v2_admin_user_list_get.assert_called_with(
        skip=0, limit=50, session_token="session_token"
    )

    assert len(user_detail_list) == 5
    assert user_detail_list[0].user_attributes.user_name == "agentservice"
    assert user_detail_list[1].user_system_info.id == 9826885173258


@pytest.mark.asyncio
async def test_list_all_user_details(user_api, user_service):
    user_api.v2_admin_user_list_get = AsyncMock()
    user_api.v2_admin_user_list_get.return_value = (
        get_deserialized_object_from_resource(
            V2UserDetailList, "user/list_user_detail.json"
        )
    )

    gen = await user_service.list_all_user_details()
    user_detail_list = [u async for u in gen]

    user_api.v2_admin_user_list_get.assert_called_with(
        skip=0, limit=50, session_token="session_token"
    )

    assert len(user_detail_list) == 5
    assert user_detail_list[0].user_attributes.user_name == "agentservice"
    assert user_detail_list[1].user_system_info.id == 9826885173258


@pytest.mark.asyncio
async def test_list_user_details_by_filter(user_api, user_service):
    user_api.v1_admin_user_find_post = AsyncMock()
    user_api.v1_admin_user_find_post.return_value = (
        get_deserialized_object_from_resource(
            UserDetailList, "user/list_user_by_filter.json"
        )
    )
    user_filter = UserFilter(status="ENABLED", role="INDIVIDUAL")

    user_detail_list = await user_service.list_user_details_by_filter(user_filter)

    user_api.v1_admin_user_find_post.assert_called_with(
        skip=0, limit=50, payload=user_filter, session_token="session_token"
    )

    assert len(user_detail_list) == 3
    assert user_detail_list[0].user_attributes.user_name == "agentservice"
    assert user_detail_list[1].user_system_info.id == 9826885173258


@pytest.mark.asyncio
async def test_list_all_user_details_by_filter(user_api, user_service):
    user_api.v1_admin_user_find_post = AsyncMock()
    user_api.v1_admin_user_find_post.return_value = (
        get_deserialized_object_from_resource(
            UserDetailList, "user/list_user_by_filter.json"
        )
    )
    user_filter = UserFilter(status="ENABLED")

    gen = await user_service.list_all_user_details_by_filter(user_filter)
    user_detail_list = [u async for u in gen]

    user_api.v1_admin_user_find_post.assert_called_with(
        skip=0, limit=50, payload=user_filter, session_token="session_token"
    )

    assert len(user_detail_list) == 3
    assert user_detail_list[0].user_attributes.user_name == "agentservice"
    assert user_detail_list[1].user_system_info.id == 9826885173258


@pytest.mark.asyncio
async def test_add_role(user_api, user_service):
    user_api.v1_admin_user_uid_roles_add_post = AsyncMock()

    await user_service.add_role(1234, RoleId.INDIVIDUAL)

    user_api.v1_admin_user_uid_roles_add_post.assert_called_with(
        uid=1234, payload=StringId(id="INDIVIDUAL"), session_token="session_token"
    )


@pytest.mark.asyncio
async def test_list_roles(system_api, user_service):
    system_api.v1_admin_system_roles_list_get = AsyncMock()
    system_api.v1_admin_system_roles_list_get.return_value = (
        get_deserialized_object_from_resource(RoleDetailList, "user/list_roles.json")
    )

    role_list = await user_service.list_roles()

    system_api.v1_admin_system_roles_list_get.assert_called_with(
        session_token="session_token"
    )

    assert len(role_list) == 12
    assert role_list[0].id == "CONTENT_MANAGEMENT"
    assert role_list[1].id == "COMPLIANCE_OFFICER"


@pytest.mark.asyncio
async def test_remove_role(user_api, user_service):
    user_api.v1_admin_user_uid_roles_remove_post = AsyncMock()

    await user_service.remove_role(1234, RoleId.INDIVIDUAL)

    user_api.v1_admin_user_uid_roles_remove_post.assert_called_with(
        uid=1234, payload=StringId(id="INDIVIDUAL"), session_token="session_token"
    )


@pytest.mark.asyncio
async def test_get_avatar(user_api, user_service):
    user_api.v1_admin_user_uid_avatar_get = AsyncMock()
    user_api.v1_admin_user_uid_avatar_get.return_value = (
        get_deserialized_object_from_resource(AvatarList, "user/list_avatar.json")
    )

    avatar_list = await user_service.get_avatar(1234)

    user_api.v1_admin_user_uid_avatar_get.assert_called_with(
        uid=1234, session_token="session_token"
    )

    assert len(avatar_list) == 5
    assert avatar_list[0].size == "600"
    assert (
        avatar_list[1].url
        == "../avatars/acme/150/7215545057281/3gXMhglCCTwLPL9JAprnyHzYn5-PR49-wYDG814n1g8.png"
    )


@pytest.mark.asyncio
async def test_update_avatar(user_api, user_service):
    user_api.v1_admin_user_uid_avatar_update_post = AsyncMock()

    await user_service.update_avatar(1234, "image_string")
    user_api.v1_admin_user_uid_avatar_update_post.assert_called_with(
        uid=1234,
        payload=AvatarUpdate(image="image_string"),
        session_token="session_token",
    )

    with open(
        get_resource_filepath("user/FINOS_icon_rgb.png", as_text=True), "rb"
    ) as file:
        avatar_bytes = file.read()
        await user_service.update_avatar(1234, avatar_bytes)

        user_api.v1_admin_user_uid_avatar_update_post.assert_called_with(
            uid=1234,
            payload=AvatarUpdate(image=str(base64.standard_b64encode(avatar_bytes))),
            session_token="session_token",
        )


@pytest.mark.asyncio
async def test_get_disclaimer(user_api, user_service):
    user_api.v1_admin_user_uid_disclaimer_get = AsyncMock()
    user_api.v1_admin_user_uid_disclaimer_get.return_value = (
        get_deserialized_object_from_resource(Disclaimer, "disclaimer/disclaimer.json")
    )

    disclaimer = await user_service.get_disclaimer(1234)

    user_api.v1_admin_user_uid_disclaimer_get.assert_called_with(
        uid=1234, session_token="session_token"
    )

    assert disclaimer.id == "571d2052e4b042aaf06d2e7a"
    assert disclaimer.name == "Enterprise Disclaimer"


@pytest.mark.asyncio
async def test_remove_disclaimer(user_api, user_service):
    user_api.v1_admin_user_uid_disclaimer_delete = AsyncMock()

    await user_service.remove_disclaimer(1234)

    user_api.v1_admin_user_uid_disclaimer_delete.assert_called_with(
        uid=1234, session_token="session_token"
    )


@pytest.mark.asyncio
async def test_add_disclaimer(user_api, user_service):
    user_api.v1_admin_user_uid_disclaimer_update_post = AsyncMock()

    await user_service.add_disclaimer(1234, "disclaimer_id")

    user_api.v1_admin_user_uid_disclaimer_update_post.assert_called_with(
        uid=1234, payload=StringId(id="disclaimer_id"), session_token="session_token"
    )


@pytest.mark.asyncio
async def test_get_delegates(user_api, user_service):
    user_api.v1_admin_user_uid_delegates_get = AsyncMock()
    user_api.v1_admin_user_uid_delegates_get.return_value = deserialize_object(
        IntegerList, "[7215545078461]"
    )

    delegate_list = await user_service.get_delegates(1234)

    user_api.v1_admin_user_uid_delegates_get.assert_called_with(
        uid=1234, session_token="session_token"
    )

    assert len(delegate_list) == 1
    assert delegate_list[0] == 7215545078461


@pytest.mark.asyncio
async def test_update_delegates(user_api, user_service):
    user_api.v1_admin_user_uid_delegates_update_post = AsyncMock()

    await user_service.update_delegates(
        7215545078541, 7215545078461, DelegateActionEnum.ADD
    )

    user_api.v1_admin_user_uid_delegates_update_post.assert_called_with(
        uid=7215545078541,
        payload=DelegateAction(
            user_id=7215545078461, action=DelegateActionEnum.ADD.value
        ),
        session_token="session_token",
    )


@pytest.mark.asyncio
async def test_get_feature_entitlements(user_api, user_service):
    user_api.v1_admin_user_uid_features_get = AsyncMock()
    user_api.v1_admin_user_uid_features_get.return_value = deserialize_object(
        FeatureList,
        payload="["
        "   {"
        '       "entitlment": "canCreatePublicRoom",'
        '       "enabled": true},'
        "   {   "
        '       "entitlment": "isExternalRoomEnabled",'
        '       "enabled": false'
        "   }"
        "]",
    )

    feature_list = await user_service.get_feature_entitlements(1234)

    user_api.v1_admin_user_uid_features_get.assert_called_with(
        uid=1234, session_token="session_token"
    )

    assert len(feature_list) == 2
    assert feature_list[0].entitlment == "canCreatePublicRoom"
    assert not feature_list[1].enabled


@pytest.mark.asyncio
async def test_update_feature_entitlements(user_api, user_service):
    user_api.v1_admin_user_uid_features_update_post = AsyncMock()
    feature = Feature(entitlment="canCreatePublicRoom", enabled=True)

    await user_service.update_feature_entitlements(1234, [feature])

    user_api.v1_admin_user_uid_features_update_post.assert_called_with(
        uid=1234, payload=FeatureList(value=[feature]), session_token="session_token"
    )


@pytest.mark.asyncio
async def test_get_status(user_api, user_service):
    user_api.v1_admin_user_uid_status_get = AsyncMock()
    user_api.v1_admin_user_uid_status_get.return_value = deserialize_object(
        UserStatus, '{"status": "ENABLED"}'
    )

    status = await user_service.get_status(1234)

    user_api.v1_admin_user_uid_status_get.assert_called_with(
        uid=1234, session_token="session_token"
    )

    assert status.status == "ENABLED"


@pytest.mark.asyncio
async def test_update_status(user_api, user_service):
    user_api.v1_admin_user_uid_status_update_post = AsyncMock()
    status = UserStatus(status="ENABLED")

    await user_service.update_status(1234, status)

    user_api.v1_admin_user_uid_status_update_post.assert_called_with(
        uid=1234, payload=status, session_token="session_token"
    )


@pytest.mark.asyncio
async def test_list_user_followers(user_api, user_service):
    user_api.v1_user_uid_followers_get = AsyncMock()
    user_api.v1_user_uid_followers_get.return_value = (
        get_deserialized_object_from_resource(
            FollowersListResponse, "user/list_user_followers.json"
        )
    )

    follower_list = await user_service.list_user_followers(1234, before=4, after=1)

    user_api.v1_user_uid_followers_get.assert_called_with(
        uid=1234, limit=100, session_token="session_token", before=4, after=1
    )

    assert follower_list.count == 5
    assert follower_list.followers[0] == 13056700579848
    assert follower_list.followers[1] == 13056700580889


@pytest.mark.asyncio
async def test_list_all_user_followers(user_api, user_service):
    user_api.v1_user_uid_followers_get = AsyncMock()
    user_api.v1_user_uid_followers_get.return_value = (
        get_deserialized_object_from_resource(
            FollowersListResponse, "user/list_user_followers.json"
        )
    )

    gen = await user_service.list_all_user_followers(1234, max_number=2)
    follower_list = [uid async for uid in gen]

    user_api.v1_user_uid_followers_get.assert_called_with(
        uid=1234,
        limit=100,
        session_token="session_token",
    )

    assert len(follower_list) == 2
    assert follower_list[0] == 13056700579848
    assert follower_list[1] == 13056700580889


@pytest.mark.asyncio
async def test_list_users_following(user_api, user_service):
    user_api.v1_user_uid_following_get = AsyncMock()
    user_api.v1_user_uid_following_get.return_value = (
        get_deserialized_object_from_resource(
            FollowingListResponse, "user/list_users_following.json"
        )
    )

    following_user_list = await user_service.list_users_following(
        1234, before=4, after=1
    )

    user_api.v1_user_uid_following_get.assert_called_with(
        uid=1234, limit=100, session_token="session_token", before=4, after=1
    )

    assert following_user_list.count == 3
    assert following_user_list.following[0] == 13056700580888
    assert following_user_list.following[1] == 13056700580889


@pytest.mark.asyncio
async def test_list_all_users_following(user_api, user_service):
    user_api.v1_user_uid_following_get = AsyncMock()
    user_api.v1_user_uid_following_get.return_value = (
        get_deserialized_object_from_resource(
            FollowingListResponse, "user/list_users_following.json"
        )
    )

    gen = await user_service.list_all_users_following(1234, max_number=2)
    following_user_list = [uid async for uid in gen]

    user_api.v1_user_uid_following_get.assert_called_with(
        uid=1234, limit=100, session_token="session_token"
    )

    assert len(following_user_list) == 2
    assert following_user_list[0] == 13056700580888
    assert following_user_list[1] == 13056700580889


@pytest.mark.asyncio
async def test_create(user_api, user_service):
    user_api.v2_admin_user_create_post = AsyncMock()
    user_api.v2_admin_user_create_post.return_value = (
        get_deserialized_object_from_resource(V2UserDetail, "user/user_detail.json")
    )

    user_create = V2UserCreate()
    user_detail = await user_service.create(user_create)

    user_api.v2_admin_user_create_post.assert_called_with(
        payload=user_create, session_token="session_token"
    )

    assert user_detail.user_attributes.user_name == "johndoe"
    assert user_detail.user_system_info.status == "ENABLED"
    assert len(user_detail.roles.value) == 6


@pytest.mark.asyncio
async def test_update(user_api, user_service):
    user_api.v2_admin_user_uid_update_post = AsyncMock()
    user_api.v2_admin_user_uid_update_post.return_value = (
        get_deserialized_object_from_resource(V2UserDetail, "user/user_detail.json")
    )

    user_attribute = V2UserAttributes()

    user_detail = await user_service.update(1234, user_attribute)

    user_api.v2_admin_user_uid_update_post.assert_called_with(
        uid=1234, payload=user_attribute, session_token="session_token"
    )

    assert user_detail.user_attributes.user_name == "johndoe"
    assert user_detail.user_system_info.status == "ENABLED"
    assert len(user_detail.roles.value) == 6


@pytest.mark.asyncio
async def test_list_audit_trail(audit_trail_api, user_service):
    audit_trail_api.v1_audittrail_privilegeduser_get = AsyncMock()
    audit_trail_api.v1_audittrail_privilegeduser_get.return_value = (
        get_deserialized_object_from_resource(
            V1AuditTrailInitiatorList, "user/list_audit_trail.json"
        )
    )

    audit_trail_initiator_list = await user_service.list_audit_trail(
        1234, 2345, 12345, RoleId.SUPER_ADMINISTRATOR, before=1, after=4
    )

    audit_trail_api.v1_audittrail_privilegeduser_get.assert_called_with(
        start_timestamp=1234,
        end_timestamp=2345,
        initiator_id=12345,
        role="SUPER_ADMINISTRATOR",
        before=1,
        after=4,
        limit=50,
        session_token="session_token",
        key_manager_token="km_token",
    )

    assert len(audit_trail_initiator_list.items) == 2
    assert audit_trail_initiator_list.items[0].initiator_id == 1353716993


@pytest.mark.asyncio
async def test_list_all_user_audit_trail(audit_trail_api, user_service):
    audit_trail_api.v1_audittrail_privilegeduser_get = AsyncMock()
    audit_trail_api.v1_audittrail_privilegeduser_get.return_value = (
        get_deserialized_object_from_resource(
            V1AuditTrailInitiatorList, "user/list_all_audit_trail_one_page.json"
        )
    )

    gen = await user_service.list_all_audit_trail(
        start_timestamp=2345,
        end_timestamp=12345,
        initiator_id=1234,
        role=RoleId.SUPER_ADMINISTRATOR,
        chunk_size=2,
        max_number=2,
    )
    audit_trail_list = [audit async for audit in gen]

    audit_trail_api.v1_audittrail_privilegeduser_get.assert_called_with(
        start_timestamp=2345,
        end_timestamp=12345,
        initiator_id=1234,
        role="SUPER_ADMINISTRATOR",
        limit=2,
        session_token="session_token",
        key_manager_token="km_token",
    )

    assert len(audit_trail_list) == 2
    assert audit_trail_list[0]["action_name"] == "profileInfoUpdate"
    assert audit_trail_list[1]["action_name"] == "userAppEntitlementInstall"


@pytest.mark.asyncio
async def test_list_all_user_audit_trail_2_pages(audit_trail_api, user_service):
    audit_trail_api.v1_audittrail_privilegeduser_get = AsyncMock()

    return_values = [
        get_deserialized_object_from_resource(
            V1AuditTrailInitiatorList, "user/list_all_audit_trail_page_1.json"
        ),
        get_deserialized_object_from_resource(
            V1AuditTrailInitiatorList, "user/list_all_audit_trail_page_2.json"
        ),
    ]

    audit_trail_api.v1_audittrail_privilegeduser_get.side_effect = return_values

    gen = await user_service.list_all_audit_trail(
        start_timestamp=2345,
        end_timestamp=12345,
        initiator_id=1234,
        role=RoleId.SUPER_ADMINISTRATOR,
        chunk_size=2,
        max_number=4,
    )
    audit_trail_list = [audit async for audit in gen]

    args, kwargs = audit_trail_api.v1_audittrail_privilegeduser_get.call_args

    assert audit_trail_api.v1_audittrail_privilegeduser_get.call_count == 2
    assert kwargs["after"] == "2"
    assert len(audit_trail_list) == 4
    assert audit_trail_list[0]["action_name"] == "profileInfoUpdate-2"
    assert audit_trail_list[1]["action_name"] == "userAppEntitlementInstall-2"
    assert audit_trail_list[2]["action_name"] == "profileInfoUpdate"
    assert audit_trail_list[3]["action_name"] == "userAppEntitlementInstall"


@pytest.mark.asyncio
async def test_suspend_user(user_api, user_service):
    user_api.v1_admin_user_user_id_suspension_update_put = AsyncMock()
    user_suspension = UserSuspension(
        suspended=True, suspended_until=1601596799999, suspension_reason="testing"
    )

    await user_service.suspend_user(1234, user_suspension)

    user_api.v1_admin_user_user_id_suspension_update_put.assert_called_with(
        user_id=1234, payload=user_suspension, session_token="session_token"
    )


@pytest.mark.asyncio
async def test_suspend(user_api, user_service):
    user_api.v1_admin_user_user_id_suspension_update_put = AsyncMock()
    user_suspension = UserSuspension(
        suspended=True, suspended_until=1601596799999, suspension_reason="testing"
    )

    await user_service.suspend(user_id=1234, reason="testing", until=1601596799999)

    user_api.v1_admin_user_user_id_suspension_update_put.assert_called_with(
        user_id=1234, payload=user_suspension, session_token="session_token"
    )


@pytest.mark.asyncio
async def test_unsuspend(user_api, user_service):
    user_api.v1_admin_user_user_id_suspension_update_put = AsyncMock()
    user_suspension = UserSuspension(suspended=False)

    await user_service.unsuspend(1234)

    user_api.v1_admin_user_user_id_suspension_update_put.assert_called_with(
        user_id=1234, payload=user_suspension, session_token="session_token"
    )


@pytest.mark.asyncio
async def test_get_manifest(user_api, user_service):
    user_api.v1_user_manifest_own_get = AsyncMock()

    await user_service.get_manifest()

    user_api.v1_user_manifest_own_get.assert_called_with(session_token="session_token")


@pytest.mark.asyncio
async def test_update_manifest_file(user_api, user_service):
    expected_manifest_data = {
        "commands": [
            {
                "args": [{"name": "[query1]"}, {"name": "[query2]"}],
                "desc": "Search users based on name, company or job title",
                "example": "/search John Smith",
                "name": "search",
            }
        ]
    }
    mock_file_content_json = json.dumps(expected_manifest_data)

    with patch(
        "pathlib.Path.open", new_callable=mock_open, read_data=mock_file_content_json
    ) as mock_path_open:
        user_api.v1_user_manifest_own_post = AsyncMock()

        await user_service.update_manifest_from_file()
        mock_path_open.assert_called_once()

        user_api.v1_user_manifest_own_post.assert_called_once_with(
            session_token="session_token",
            manifest=ServiceAccountManifest(json.dumps(expected_manifest_data)),
        )
