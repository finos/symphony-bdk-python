from unittest.mock import AsyncMock, MagicMock

import pytest

from symphony.bdk.core.service.version.agent_version_service import AgentVersionService
from symphony.bdk.gen.agent_model.agent_info import AgentInfo
from symphony.bdk.gen.exceptions import ApiException


@pytest.fixture
def signals_api():
    return AsyncMock()


@pytest.fixture
def retry_config():
    return MagicMock()


@pytest.fixture
def service(signals_api, retry_config):
    return AgentVersionService(signals_api, retry_config)


@pytest.mark.parametrize(
    "version_string, expected_major, expected_minor",
    [
        # Given: Agent version string
        ("Agent-24.12.0", 24, 12),
        ("Agent-25.0.0-SNAPSHOT", 25, 0),
        ("Agent-100.1.23", 100, 1),
        ("NotAnAgent-1.0.0", None, None),
        ("Agent-24", None, None),
        ("Agent-24.12", None, None),
        ("some random string", None, None),
        (None, None, None),
    ],
)
def test_parse_version(version_string, expected_major, expected_minor):
    # When: agent parser is called
    major, minor = AgentVersionService._parse_version(version_string)
    # Then: major and minor version are extracted correctly
    assert major == expected_major
    assert minor == expected_minor


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "agent_version, expected_result",
    [
        ("Agent-24.12.0", True),  # Exact minimum version
        ("Agent-24.13.0", True),  # Minor version greater
        ("Agent-25.0.0", True),  # Major version greater
        ("Agent-24.11.0", False),  # Minor version smaller
        ("Agent-23.15.0", False),  # Major version smaller
        ("Malformed-Version-String", False),  # Malformed string
    ],
)
async def test_is_skd_supported_versions(
    service, signals_api, agent_version, expected_result
):
    """Tests the SKD support check against various agent version strings."""
    # Given: Agent version string is returned from info API
    signals_api.v1_info_get.return_value = AgentInfo(version=agent_version)
    # When: is_skd_supported is called
    is_supported = await service.is_skd_supported()
    # Then: the expected boolean result is returned
    assert is_supported is expected_result
    signals_api.v1_info_get.assert_called_once()


@pytest.mark.asyncio
async def test_is_skd_supported_api_exception(service, signals_api):
    """Tests that SKD support is False when the agent API call fails."""
    # Given: The call to the agent info API will raise an exception
    signals_api.v1_info_get.side_effect = ApiException(reason="Agent unavailable")
    # When: is_skd_supported is called
    is_supported = await service.is_skd_supported()
    # Then: False is returned and exception is handled
    assert is_supported is False
    signals_api.v1_info_get.assert_called_once()


@pytest.mark.asyncio
async def test_is_skd_supported_no_version_in_response(service, signals_api):
    """Tests that SKD support is False when the agent info response is missing a version."""
    # Given: The agent info API returns a response with a null version
    signals_api.v1_info_get.return_value = AgentInfo(version=None)
    # When: is_skd_supported is called
    is_supported = await service.is_skd_supported()
    # Then: False is returned
    assert is_supported is False
