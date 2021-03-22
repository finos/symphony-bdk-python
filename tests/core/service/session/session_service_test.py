from unittest.mock import MagicMock, AsyncMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.gen.pod_api.session_api import SessionApi
from tests.utils.resource_utils import object_from_json_relative_path


@pytest.fixture(name="auth_session")
def fixture_auth_session():
    auth_session = AuthSession(None)
    auth_session.session_token = "session_token"
    auth_session.key_manager_token = "km_token"
    return auth_session


@pytest.fixture(name="session_api")
def fixture_session_api():
    return MagicMock(SessionApi)


@pytest.fixture(name="session_service")
def fixture_session_service(session_api, auth_session):
    service = SessionService(
        session_api,
        auth_session
    )
    return service


@pytest.mark.asyncio
async def test_get_session(session_api, session_service):
    session_api.v2_sessioninfo_get = AsyncMock()
    session_api.v2_sessioninfo_get.return_value = object_from_json_relative_path("session/get_session.json")

    session = await session_service.get_session()
    assert session.display_name == "Symphony Admin"


