from unittest.mock import MagicMock, AsyncMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.gen.pod_api.session_api import SessionApi
from symphony.bdk.gen.pod_model.user_v2 import UserV2
from tests.utils.resource_utils import get_deserialized_object_from_resource
from tests.core.retry import minimal_retry_config


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
        auth_session,
        minimal_retry_config()
    )
    return service


@pytest.mark.asyncio
async def test_get_session(session_api, session_service):
    session_api.v2_sessioninfo_get = AsyncMock()
    session_api.v2_sessioninfo_get.return_value = get_deserialized_object_from_resource(UserV2,
                                                                                        "session/get_session.json")

    session = await session_service.get_session()
    assert session.display_name == "Symphony Admin"
