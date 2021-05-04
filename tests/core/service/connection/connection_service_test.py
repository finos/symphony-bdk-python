from unittest.mock import MagicMock, AsyncMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.connection.connection_service import ConnectionService
from symphony.bdk.core.service.connection.model.connection_status import ConnectionStatus
from symphony.bdk.gen.pod_api.connection_api import ConnectionApi
from symphony.bdk.gen.pod_model.user_connection import UserConnection
from symphony.bdk.gen.pod_model.user_connection_list import UserConnectionList
from symphony.bdk.gen.pod_model.user_connection_request import UserConnectionRequest
from tests.core.config import minimal_retry_config
from tests.utils.resource_utils import deserialize_object


@pytest.fixture(name="auth_session")
def fixture_auth_session():
    bot_session = AuthSession(None)
    bot_session.session_token = "session_token"
    bot_session.key_manager_token = "km_token"
    return bot_session


@pytest.fixture(name="connection_api")
def fixture_connection_api():
    return MagicMock(ConnectionApi)


@pytest.fixture(name="connection_service")
def fixture_connection_service(connection_api, auth_session):
    service = ConnectionService(
        connection_api,
        auth_session,
        minimal_retry_config()
    )
    return service


@pytest.mark.asyncio
async def test_get_connection(connection_api, connection_service):
    connection_api.v1_connection_user_user_id_info_get = AsyncMock()
    connection_api.v1_connection_user_user_id_info_get.return_value = \
        deserialize_object(UserConnection, "{"
                                           "   \"userId\": 769658112378,"
                                           "   \"status\": \"ACCEPTED\""
                                           "}")

    user_connection = await connection_service.get_connection(769658112378)

    connection_api.v1_connection_user_user_id_info_get.assert_called_with(
        user_id="769658112378",
        session_token="session_token"
    )
    assert user_connection.user_id == 769658112378
    assert user_connection.status == ConnectionStatus.ACCEPTED.value


@pytest.mark.asyncio
async def test_list_connections(connection_api, connection_service):
    connection_api.v1_connection_list_get = AsyncMock()
    connection_api.v1_connection_list_get.return_value = deserialize_object(UserConnectionList,
                                                                            "["
                                                                            "   {"
                                                                            "       \"userId\": 7078106126503,"
                                                                            "       \"status\": \"PENDING_OUTGOING\","
                                                                            "       \"updatedAt\": 1471018076255"
                                                                            "   },"
                                                                            "   {"
                                                                            "       \"userId\": 7078106103809,"
                                                                            "       \"status\": \"PENDING_INCOMING\","
                                                                            "       \"updatedAt\": 1467562406219"
                                                                            "   }"
                                                                            "]")

    user_connections = await connection_service.list_connections(ConnectionStatus.ALL, [7078106126503, 7078106103809])

    connection_api.v1_connection_list_get.assert_called_with(
        user_ids="7078106126503,7078106103809",
        status=ConnectionStatus.ALL.value,
        session_token="session_token"
    )

    assert len(user_connections) == 2
    assert user_connections[0].user_id == 7078106126503
    assert user_connections[1].status == ConnectionStatus.PENDING_INCOMING.value


@pytest.mark.asyncio
async def test_create_connection(connection_api, connection_service):
    connection_api.v1_connection_create_post = AsyncMock()
    connection_api.v1_connection_create_post.return_value = deserialize_object(UserConnection,
                                                                               "{"
                                                                               "  \"userId\": 7078106126503,"
                                                                               "  \"status\": \"PENDING_OUTGOING\","
                                                                               "  \"firstRequestedAt\": 1471018076255,"
                                                                               "  \"updatedAt\": 1471018076255,"
                                                                               "  \"requestCounter\": 1"
                                                                               "}")

    user_connection = await connection_service.create_connection(7078106126503)

    connection_api.v1_connection_create_post.assert_called_with(
        connection_request=UserConnectionRequest(user_id=7078106126503),
        session_token="session_token"
    )

    assert user_connection.user_id == 7078106126503
    assert user_connection.request_counter == 1
    assert user_connection.status == ConnectionStatus.PENDING_OUTGOING.value


@pytest.mark.asyncio
async def test_accept_connection(connection_api, connection_service):
    connection_api.v1_connection_accept_post = AsyncMock()
    connection_api.v1_connection_accept_post.return_value = deserialize_object(UserConnection,
                                                                               "{"
                                                                               "   \"userId\": 7078106169577,"
                                                                               "   \"status\": \"ACCEPTED\","
                                                                               "   \"firstRequestedAt\": 1471046357339,"
                                                                               "   \"updatedAt\": 1471046517684,"
                                                                               "   \"requestCounter\": 1"
                                                                               "}")

    user_connection = await connection_service.accept_connection(7078106169577)

    connection_api.v1_connection_accept_post.assert_called_with(
        connection_request=UserConnectionRequest(user_id=7078106169577),
        session_token="session_token"
    )

    assert user_connection.user_id == 7078106169577
    assert user_connection.first_requested_at == 1471046357339
    assert user_connection.status == ConnectionStatus.ACCEPTED.value


@pytest.mark.asyncio
async def test_reject_connection(connection_api, connection_service):
    connection_api.v1_connection_reject_post = AsyncMock()
    connection_api.v1_connection_reject_post.return_value = deserialize_object(UserConnection,
                                                                               "{"
                                                                               "   \"userId\": 7215545059385,"
                                                                               "   \"status\": \"REJECTED\","
                                                                               "   \"firstRequestedAt\": 1471044955409,"
                                                                               "   \"updatedAt\": 1471045390420,"
                                                                               "   \"requestCounter\": 1"
                                                                               "}")

    user_connection = await connection_service.reject_connection(7215545059385)

    connection_api.v1_connection_reject_post.assert_called_with(
        connection_request=UserConnectionRequest(user_id=7215545059385),
        session_token="session_token"
    )

    assert user_connection.user_id == 7215545059385
    assert user_connection.status == ConnectionStatus.REJECTED.value


@pytest.mark.asyncio
async def test_remove_connection(connection_api, connection_service):
    connection_api.v1_connection_user_uid_remove_post = AsyncMock()

    await connection_service.remove_connection(1234)

    connection_api.v1_connection_user_uid_remove_post.assert_called_with(
        uid=1234,
        session_token="session_token"
    )
