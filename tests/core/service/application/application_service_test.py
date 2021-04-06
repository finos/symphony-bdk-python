from unittest.mock import MagicMock, AsyncMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.application.application_service import ApplicationService
from symphony.bdk.gen.pod_api.app_entitlement_api import AppEntitlementApi
from symphony.bdk.gen.pod_api.application_api import ApplicationApi
from symphony.bdk.gen.pod_model.application_detail import ApplicationDetail
from symphony.bdk.gen.pod_model.pod_app_entitlement import PodAppEntitlement
from symphony.bdk.gen.pod_model.pod_app_entitlement_list import PodAppEntitlementList
from symphony.bdk.gen.pod_model.user_app_entitlement import UserAppEntitlement
from symphony.bdk.gen.pod_model.user_app_entitlement_list import UserAppEntitlementList
from tests.utils.resource_utils import object_from_json_relative_path, object_from_json


@pytest.fixture(name="auth_session")
def fixture_auth_session():
    bot_session = AuthSession(None)
    bot_session.session_token = "session_token"
    bot_session.key_manager_token = "km_token"
    return bot_session


@pytest.fixture(name="application_api")
def fixture_application_api():
    return MagicMock(ApplicationApi)


@pytest.fixture(name="app_entitlement_api")
def fixture_app_entitlement_api():
    return MagicMock(AppEntitlementApi)


@pytest.fixture(name="application_service")
def fixture_application_service(application_api, app_entitlement_api, auth_session):
    service = ApplicationService(application_api, app_entitlement_api, auth_session)
    return service


@pytest.mark.asyncio
async def test_create_application(application_api, application_service):
    application_api.v1_admin_app_create_post = AsyncMock()
    application_api.v1_admin_app_create_post.return_value = \
        object_from_json_relative_path("application/create_application.json")

    application_detail = await application_service.create_application(ApplicationDetail())

    application_api.v1_admin_app_create_post.assert_called_with(
        session_token="session_token",
        application_detail=ApplicationDetail()
    )

    assert application_detail.applicationInfo.appId == "my-test-app"
    assert application_detail.description == "a test app"


@pytest.mark.asyncio
async def test_update_application(application_api, application_service):
    application_api.v1_admin_app_id_update_post = AsyncMock()
    application_api.v1_admin_app_id_update_post.return_value = \
        object_from_json_relative_path("application/update_application.json")

    application_detail = await application_service.update_application("my-test-app", ApplicationDetail())

    application_api.v1_admin_app_id_update_post.assert_called_with(
        session_token="session_token",
        id="my-test-app",
        application_detail=ApplicationDetail()
    )

    assert application_detail.applicationInfo.appId == "my-test-app"
    assert application_detail.description == "updating an app"


@pytest.mark.asyncio
async def test_delete_application(application_api, application_service):
    application_api.v1_admin_app_id_delete_post = AsyncMock()
    application_api.v1_admin_app_id_delete_post.return_value = object_from_json(
        "{"
        "   \"format\": \"TEXT\","
        "   \"message\": \"OK\""
        "}"
    )

    await application_service.delete_application("my-test-app")

    application_api.v1_admin_app_id_delete_post.assert_called_with(
        session_token="session_token",
        id="my-test-app"
    )


@pytest.mark.asyncio
async def test_get_application(application_api, application_service):
    application_api.v1_admin_app_id_get_get = AsyncMock()
    application_api.v1_admin_app_id_get_get.return_value =\
        object_from_json_relative_path("application/get_application.json")

    application_detail = await application_service.get_application("my-test-app")

    application_api.v1_admin_app_id_get_get.assert_called_with(
        session_token="session_token",
        id="my-test-app"
    )

    assert application_detail.applicationInfo.appId == "my-test-app"
    assert application_detail.description == "get an app"


@pytest.mark.asyncio
async def test_list_application_entitlements(app_entitlement_api, application_service):
    app_entitlement_api.v1_admin_app_entitlement_list_get = AsyncMock()
    app_entitlement_api.v1_admin_app_entitlement_list_get.return_value = \
        object_from_json_relative_path("application/list_app_entitlements.json")

    pod_app_entitlements = await application_service.list_application_entitlements()

    app_entitlement_api.v1_admin_app_entitlement_list_get.assert_called_with(
        session_token="session_token"
    )

    assert len(pod_app_entitlements) == 3
    assert pod_app_entitlements[0].appId == "djApp"


@pytest.mark.asyncio
async def test_update_application_entitlements(app_entitlement_api, application_service):
    app_entitlement_api.v1_admin_app_entitlement_list_post = AsyncMock()
    app_entitlement_api.v1_admin_app_entitlement_list_post.return_value = \
        object_from_json_relative_path("application/update_app_entitlements.json")

    pod_app_entitlement = PodAppEntitlement(
        app_id="rsa-app-auth-example",
        app_name="App Auth RSA Example",
        enable=True,
        listed=True,
        install=False
    )
    pod_app_entitlements = await application_service.update_application_entitlements([pod_app_entitlement])

    app_entitlement_api.v1_admin_app_entitlement_list_post.assert_called_with(
        session_token="session_token",
        payload=PodAppEntitlementList(value=[pod_app_entitlement])
    )

    assert len(pod_app_entitlements) == 1
    assert pod_app_entitlements[0].appId == "rsa-app-auth-example"


@pytest.mark.asyncio
async def test_list_user_applications(app_entitlement_api, application_service):
    app_entitlement_api.v1_admin_user_uid_app_entitlement_list_get = AsyncMock()
    app_entitlement_api.v1_admin_user_uid_app_entitlement_list_get.return_value =\
        object_from_json_relative_path("application/list_user_apps.json")

    user_app_entitlements = await application_service.list_user_applications(1234)

    app_entitlement_api.v1_admin_user_uid_app_entitlement_list_get.assert_called_with(
        session_token="session_token",
        uid=1234
    )

    assert len(user_app_entitlements) == 3
    assert user_app_entitlements[0].appId == "djApp"


@pytest.mark.asyncio
async def test_update_user_applications(app_entitlement_api, application_service):
    app_entitlement_api.v1_admin_user_uid_app_entitlement_list_post = AsyncMock()
    app_entitlement_api.v1_admin_user_uid_app_entitlement_list_post.return_value = \
        object_from_json_relative_path("application/list_user_apps.json")

    user_app_entitlement = UserAppEntitlement(
        app_id="djApp",
        listed=True,
        install=False
    )

    user_app_entitlements = await application_service.update_user_applications(1234, [user_app_entitlement])

    app_entitlement_api.v1_admin_user_uid_app_entitlement_list_post.assert_called_with(
        session_token="session_token",
        uid=1234,
        payload=UserAppEntitlementList(value=[user_app_entitlement])
    )

    assert len(user_app_entitlements) == 3
    assert user_app_entitlements[0].appId == "djApp"
