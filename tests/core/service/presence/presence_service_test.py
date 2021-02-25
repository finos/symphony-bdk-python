from unittest.mock import MagicMock, AsyncMock
import pytest

from symphony.bdk.gen import ApiException
from tests.utils.resource_utils import object_from_json_relative_path

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.presence.presence_service import PresenceService

from symphony.bdk.gen.pod_api.presence_api import PresenceApi


@pytest.fixture()
def auth_session():
    bot_session = AuthSession(None)
    bot_session.session_token = 'session_token'
    bot_session.key_manager_token = 'km_token'
    return bot_session


@pytest.fixture()
def mocked_presence_api_client():
    api_client = MagicMock(PresenceApi)
    api_client.v2_user_presence_get = AsyncMock()
    api_client.v2_users_presence_get = AsyncMock()
    api_client.v3_user_uid_presence_get = AsyncMock()
    api_client.v1_user_presence_register_post = AsyncMock()
    # api_client.v2_user_presence_post = AsyncMock()
    # api_client.v1_presence_feed_create_post = AsyncMock()
    # api_client.v1_presence_feed_feed_id_read_get = AsyncMock()
    # api_client.v1_presence_feed_feed_id_delete_post = AsyncMock()
    # api_client.v3_user_presence_post = AsyncMock()
    return api_client


@pytest.fixture()
def presence_service(mocked_presence_api_client, auth_session):
    return PresenceService(mocked_presence_api_client, auth_session)


@pytest.mark.asyncio
async def test_get_presence(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v2_user_presence_get.return_value = object_from_json_relative_path(
        "presence_response/get_presence.json")

    presence = await presence_service.get_presence()

    assert presence.category == "AVAILABLE"
    assert presence.userId == 14568529068038


@pytest.mark.asyncio
async def test_get_presence_failed(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v2_user_presence_get.side_effect = ApiException(400)

    with pytest.raises(ApiException):
        await presence_service.get_presence()


@pytest.mark.asyncio
async def test_get_all_presence(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v2_users_presence_get.return_value = object_from_json_relative_path(
        "presence_response/list_presences.json")

    presence_list = await presence_service.get_all_presence(1234, 5000)

    assert len(presence_list) == 2
    assert presence_list[0].userId == 14568529068038
    assert presence_list[0].category == "AVAILABLE"
    assert presence_list[0].timestamp == 1533928483800

    assert presence_list[1].userId == 974217539631
    assert presence_list[1].category == "OFFLINE"


@pytest.mark.asyncio
async def test_get_all_presence_failed(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v2_users_presence_get.side_effect = ApiException(400)

    with pytest.raises(ApiException):
        await presence_service.get_all_presence(1234, 5000)


@pytest.mark.asyncio
async def test_get_user_presence(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v3_user_uid_presence_get.return_value = object_from_json_relative_path(
        "presence_response/get_user_presence.json")

    presence = await presence_service.get_user_presence(1234, True)

    assert presence.userId == 349871117483
    assert presence.category == "AVAILABLE"


@pytest.mark.asyncio
async def test_get_user_presence_failed(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v3_user_uid_presence.side_effect = ApiException(400)

    with pytest.raises(ApiException):
        await presence_service.get_user_presence(1234, True)


@pytest.mark.asyncio
async def test_external_presence_interest(presence_service, mocked_presence_api_client):
    uid_list = [1234]
    await presence_service.external_presence_interest(uid_list)
    mocked_presence_api_client.v1_user_presence_register_post.assert_called_once_with(session_token="session_token",
                                                                                      uid_list=uid_list)


@pytest.mark.asyncio
async def test_external_presence_interest_failed(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v1_user_presence_register_post.side_effect = ApiException(400)
    uid_list = [1234]
    with pytest.raises(ApiException):
        await presence_service.external_presence_interest(uid_list)
