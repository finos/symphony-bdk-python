from unittest.mock import AsyncMock, MagicMock

import pytest

from symphony.bdk.core.service.health.health_service import HealthService
from symphony.bdk.gen import ApiException
from symphony.bdk.gen.agent_api.signals_api import SignalsApi
from symphony.bdk.gen.agent_api.system_api import SystemApi
from symphony.bdk.gen.agent_model.agent_info import AgentInfo
from symphony.bdk.gen.agent_model.v3_health import V3Health
from tests.core.config import minimal_retry_config
from tests.utils.resource_utils import get_deserialized_object_from_resource


@pytest.fixture(name="mocked_system_api_client")
def fixture_mocked_system_api_client():
    api_client = MagicMock(SystemApi)
    api_client.v3_health = AsyncMock()
    api_client.v3_extended_health = AsyncMock()
    return api_client


@pytest.fixture(name="mocked_signals_api_client")
def fixture_mocked_signals_api_client():
    api_client = MagicMock(SignalsApi)
    api_client.v1_info_get = AsyncMock()
    return api_client


@pytest.fixture(name="health_service")
def fixture_health_service(mocked_system_api_client, mocked_signals_api_client):
    return HealthService(mocked_system_api_client, mocked_signals_api_client, minimal_retry_config)


@pytest.mark.asyncio
async def test_health_check(health_service, mocked_system_api_client):
    mocked_system_api_client.v3_health.return_value = get_deserialized_object_from_resource(
        V3Health, resource_path="health_response/health_check.json"
    )

    health = await health_service.health_check()

    assert health.status.value == "UP"


@pytest.mark.asyncio
async def test_health_check_failed(health_service, mocked_system_api_client):
    mocked_system_api_client.v3_health.side_effect = ApiException(400)

    with pytest.raises(ApiException):
        await health_service.health_check()


@pytest.mark.asyncio
async def test_health_check_extended(health_service, mocked_system_api_client):
    mocked_system_api_client.v3_extended_health.return_value = (
        get_deserialized_object_from_resource(
            V3Health, resource_path="health_response/health_check_extended.json"
        )
    )
    health = await health_service.health_check_extended()

    assert health.status.value == "UP"
    assert health.services.get("pod").version == "1.57.0"
    assert health.services.get("datafeed").status.value == "UP"
    assert health.users.get("agentservice").status.value == "UP"


@pytest.mark.asyncio
async def test_health_check_extended_failed(health_service, mocked_system_api_client):
    mocked_system_api_client.v3_extended_health.side_effect = ApiException(400)

    with pytest.raises(ApiException):
        await health_service.health_check_extended()


@pytest.mark.asyncio
async def test_get_agent_info(health_service, mocked_signals_api_client):
    mocked_signals_api_client.v1_info_get.return_value = get_deserialized_object_from_resource(
        AgentInfo, resource_path="health_response/agent_info.json"
    )

    agent_info = await health_service.get_agent_info()

    assert agent_info.hostname == "agent-75...4b6"
    assert agent_info.ip_address == "22.222.222.22"
    assert agent_info.on_prem


@pytest.mark.asyncio
async def test_get_agent_info_failed(health_service, mocked_signals_api_client):
    mocked_signals_api_client.v1_info_get.side_effect = ApiException(400)

    with pytest.raises(ApiException):
        await health_service.get_agent_info()
