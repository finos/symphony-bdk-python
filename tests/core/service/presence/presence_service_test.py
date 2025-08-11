from unittest.mock import AsyncMock, MagicMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.presence.presence_service import (
    PresenceService,
    PresenceStatus,
)
from symphony.bdk.gen import ApiException
from symphony.bdk.gen.pod_api.presence_api import PresenceApi
from symphony.bdk.gen.pod_model.string_id import StringId
from symphony.bdk.gen.pod_model.v2_presence import V2Presence
from symphony.bdk.gen.pod_model.v2_presence_list import V2PresenceList
from symphony.bdk.gen.pod_model.v2_presence_status import V2PresenceStatus
from symphony.bdk.gen.pod_model.v2_user_presence import V2UserPresence
from tests.core.config import minimal_retry_config
from tests.utils.resource_utils import deserialize_object


@pytest.fixture(name="auth_session")
def fixture_auth_session():
    bot_session = AuthSession(None)
    bot_session.session_token = "session_token"
    bot_session.key_manager_token = "km_token"
    return bot_session


@pytest.fixture(name="mocked_presence_api_client")
def fixture_mocked_presence_api_client():
    api_client = MagicMock(PresenceApi)
    api_client.v2_user_presence_get = AsyncMock()
    api_client.v2_users_presence_get = AsyncMock()
    api_client.v3_user_uid_presence_get = AsyncMock()
    api_client.v1_user_presence_register_post = AsyncMock()
    api_client.v2_user_presence_post = AsyncMock()
    api_client.v1_presence_feed_create_post = AsyncMock()
    api_client.v1_presence_feed_feed_id_read_get = AsyncMock()
    api_client.v1_presence_feed_feed_id_delete_post = AsyncMock()
    api_client.v3_user_presence_post = AsyncMock()
    return api_client


@pytest.fixture(name="presence_service")
def fixture_presence_service(mocked_presence_api_client, auth_session):
    return PresenceService(
        mocked_presence_api_client, auth_session, minimal_retry_config()
    )


@pytest.mark.asyncio
async def test_get_presence(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v2_user_presence_get.return_value = deserialize_object(
        V2Presence,
        '{"category":"AVAILABLE","userId":14568529068038,"timestamp":1533928483800}',
    )

    presence = await presence_service.get_presence()

    assert presence.category == "AVAILABLE"
    assert presence.user_id == 14568529068038


@pytest.mark.asyncio
async def test_get_presence_failed(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v2_user_presence_get.side_effect = ApiException(400)

    with pytest.raises(ApiException):
        await presence_service.get_presence()


@pytest.mark.asyncio
async def test_get_all_presence(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v2_users_presence_get.return_value = deserialize_object(
        V2PresenceList,
        "["
        "    {"
        '        "category":"AVAILABLE",'
        '        "userId":14568529068038,'
        '        "timestamp":1533928483800},'
        "    {"
        '        "category":"OFFLINE",'
        '        "userId":974217539631,'
        '        "timestamp":1503286226030'
        "    }"
        "]",
    )

    presence_list = await presence_service.get_all_presence(1234, 5000)

    mocked_presence_api_client.v2_users_presence_get.assert_called_once_with(
        session_token="session_token", last_user_id=1234, limit=5000
    )
    assert len(presence_list) == 2
    assert presence_list[0].user_id == 14568529068038
    assert presence_list[0].category == "AVAILABLE"
    assert presence_list[0].timestamp == 1533928483800
    assert presence_list[1].user_id == 974217539631
    assert presence_list[1].category == "OFFLINE"


@pytest.mark.asyncio
async def test_get_all_presence_failed(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v2_users_presence_get.side_effect = ApiException(400)

    with pytest.raises(ApiException):
        await presence_service.get_all_presence(1234, 5000)


@pytest.mark.asyncio
async def test_get_user_presence(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v3_user_uid_presence_get.return_value = (
        deserialize_object(
            V2Presence,
            '{"category":"AVAILABLE",'
            '"userId":14568529068038,'
            '"timestamp":1533928483800}',
        )
    )

    presence = await presence_service.get_user_presence(1234, True)

    mocked_presence_api_client.v3_user_uid_presence_get.assert_called_once_with(
        uid=1234, session_token="session_token", local=True
    )
    assert presence.user_id == 14568529068038
    assert presence.category == "AVAILABLE"


@pytest.mark.asyncio
async def test_get_user_presence_failed(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v3_user_uid_presence_get.side_effect = ApiException(400)

    with pytest.raises(ApiException):
        await presence_service.get_user_presence(1234, True)


@pytest.mark.asyncio
async def test_external_presence_interest(presence_service, mocked_presence_api_client):
    uid_list = [1234]
    await presence_service.external_presence_interest(uid_list)
    mocked_presence_api_client.v1_user_presence_register_post.assert_called_once_with(
        session_token="session_token", uid_list=uid_list
    )


@pytest.mark.asyncio
async def test_external_presence_interest_failed(
    presence_service, mocked_presence_api_client
):
    mocked_presence_api_client.v1_user_presence_register_post.side_effect = (
        ApiException(400)
    )
    uid_list = [1234]
    with pytest.raises(ApiException):
        await presence_service.external_presence_interest(uid_list)


@pytest.mark.asyncio
async def test_set_presence(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v2_user_presence_post.return_value = deserialize_object(
        V2Presence,
        '{"category":"AWAY","userId":14568529068038,"timestamp":1533928483800}',
    )

    presence = await presence_service.set_presence(PresenceStatus.AWAY, True)

    mocked_presence_api_client.v2_user_presence_post.assert_called_once_with(
        session_token="session_token",
        presence=V2PresenceStatus(category="AWAY"),
        soft=True,
    )
    assert presence.category == "AWAY"
    assert presence.user_id == 14568529068038


@pytest.mark.asyncio
async def test_set_presence_failed(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v2_user_presence_post.side_effect = ApiException(400)

    with pytest.raises(ApiException):
        await presence_service.set_presence(PresenceStatus.AWAY, True)


@pytest.mark.asyncio
async def test_create_presence_feed(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v1_presence_feed_create_post.return_value = (
        deserialize_object(StringId, '{"id":"c4dca251-8639-48db-a9d4-f387089e17cf"}')
    )

    feed_id = await presence_service.create_presence_feed()

    assert feed_id == "c4dca251-8639-48db-a9d4-f387089e17cf"


@pytest.mark.asyncio
async def test_create_presence_feed_failed(
    presence_service, mocked_presence_api_client
):
    mocked_presence_api_client.v1_presence_feed_create_post.side_effect = ApiException(
        400
    )

    with pytest.raises(ApiException):
        await presence_service.create_presence_feed()


@pytest.mark.asyncio
async def test_read_presence_feed(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v1_presence_feed_feed_id_read_get.return_value = (
        deserialize_object(
            V2PresenceList,
            "["
            "  {"
            '      "category":"AVAILABLE",'
            '      "userId":7078106103901,'
            '      "timestamp":1489769156271'
            "  },"
            "  {"
            '      "category":"ON_THE_PHONE",'
            '      "userId":7078106103902,'
            '      "timestamp":1489769156273'
            "  }"
            "]",
        )
    )

    feed_id = "c4dca251-8639-48db-a9d4-f387089e17cf"
    presence_list = await presence_service.read_presence_feed(feed_id)

    mocked_presence_api_client.v1_presence_feed_feed_id_read_get.assert_called_once_with(
        session_token="session_token", feed_id=feed_id
    )
    assert len(presence_list) == 2
    assert presence_list[0].category == "AVAILABLE"
    assert presence_list[0].user_id == 7078106103901
    assert presence_list[1].category == "ON_THE_PHONE"
    assert presence_list[1].user_id == 7078106103902


@pytest.mark.asyncio
async def test_read_presence_feed_failed(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v1_presence_feed_feed_id_read_get.side_effect = (
        ApiException(400)
    )

    with pytest.raises(ApiException):
        await presence_service.read_presence_feed("1234")


@pytest.mark.asyncio
async def test_delete_presence_feed(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v1_presence_feed_feed_id_delete_post.return_value = (
        deserialize_object(StringId, '{"id":"c4dca251-8639-48db-a9d4-f387089e17cf"}')
    )

    feed_id = await presence_service.delete_presence_feed(
        "c4dca251-8639-48db-a9d4-f387089e17cf"
    )

    mocked_presence_api_client.v1_presence_feed_feed_id_delete_post.assert_called_once_with(
        session_token="session_token", feed_id=feed_id
    )
    assert feed_id == "c4dca251-8639-48db-a9d4-f387089e17cf"


@pytest.mark.asyncio
async def test_delete_presence_feed_failed(
    presence_service, mocked_presence_api_client
):
    mocked_presence_api_client.v1_presence_feed_feed_id_delete_post.side_effect = (
        ApiException(400)
    )

    with pytest.raises(ApiException):
        await presence_service.delete_presence_feed("1234")


@pytest.mark.asyncio
async def test_set_user_presence(presence_service, mocked_presence_api_client):
    mocked_presence_api_client.v3_user_presence_post.return_value = deserialize_object(
        V2Presence,
        '{"category":"AWAY","userId":14568529068038,"timestamp":1533928483800}',
    )

    presence = await presence_service.set_user_presence(
        14568529068038, PresenceStatus.AWAY, True
    )

    mocked_presence_api_client.v3_user_presence_post.assert_called_once_with(
        session_token="session_token",
        presence=V2UserPresence(user_id=14568529068038, category="AWAY"),
        soft=True,
    )

    assert presence.user_id == 14568529068038
    assert presence.category == "AWAY"
