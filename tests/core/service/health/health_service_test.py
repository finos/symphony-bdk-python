from unittest.mock import MagicMock, AsyncMock
import pytest

from symphony.bdk.core.service.health.health_service import HealthService
from symphony.bdk.gen import ApiException
from symphony.bdk.gen.agent_api.system_api import SystemApi
from symphony.bdk.gen.agent_api.signals_api import SignalsApi

from tests.utils.resource_utils import object_from_json_relative_path


@pytest.fixture(name='system_api_client')
def fixture_system_api_client():
    api_client = MagicMock(SystemApi)
    api_client.v3_health = AsyncMock()
    api_client.v3_extended_health = AsyncMock()
    return api_client


@pytest.fixture(name='signals_api_client')
def fixture_signals_api_client():
    api_client = MagicMock(SignalsApi)
    api_client.v1_info_get = AsyncMock()
    return api_client


@pytest.fixture(name='health_service')
def fixture_health_service(system_api_client, signals_api_client):
    return HealthService(system_api_client, signals_api_client)


@pytest.mark.asyncio
async def test_health_check(health_service, system_api_client):
    system_api_client.v3_health.return_value = object_from_json_relative_path(
        'health_response/health_check.json')

    health = await health_service.health_check()

    assert health.status == 'UP'


@pytest.mark.asyncio
async def test_health_check_failed(health_service, system_api_client):
    system_api_client.v3_health.side_effect = ApiException(400)

    with pytest.raises(ApiException):
        await health_service.health_check()


@pytest.mark.asyncio
async def test_health_check_extended(health_service, system_api_client):
    system_api_client.v3_extended_health.return_value = object_from_json_relative_path(
        'health_response/health_check_extended.json')
    health = await health_service.health_check_extended()

    assert health.status == 'UP'
    assert health.services.pod.version == '1.57.0'
    assert health.services.datafeed.status == 'UP'
    assert health.users.agentservice.status == 'UP'


@pytest.mark.asyncio
async def test_health_check_extended_failed(health_service, system_api_client):
    system_api_client.v3_extended_health.side_effect = ApiException(400)

    with pytest.raises(ApiException):
        await health_service.health_check_extended()


@pytest.mark.asyncio
async def test_get_agent_info(health_service, signals_api_client):
    signals_api_client.v1_info_get.return_value = object_from_json_relative_path(
        'health_response/agent_info.json')

    agent_info = await health_service.get_agent_info()

    assert agent_info.hostname == 'agent-75...4b6'
    assert agent_info.ipAddress == '22.222.222.22'
    assert agent_info.onPrem


@pytest.mark.asyncio
async def test_get_agent_info_failed(health_service, signals_api_client):
    signals_api_client.v1_info_get.side_effect = ApiException(400)

    with pytest.raises(ApiException):
        await health_service.get_agent_info()
