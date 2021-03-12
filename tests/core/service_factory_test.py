from unittest.mock import MagicMock

import pytest

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.application.application_service import ApplicationService
from symphony.bdk.core.service.connection.connection_service import ConnectionService
from symphony.bdk.core.service.datafeed.datafeed_loop_v1 import DatafeedLoopV1
from symphony.bdk.core.service.datafeed.datafeed_loop_v2 import DatafeedLoopV2
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.service.presence.presence_service import PresenceService
from symphony.bdk.core.service.signal.signal_service import SignalService
from symphony.bdk.core.service.stream.stream_service import StreamService
from symphony.bdk.core.service.user.user_service import UserService
from symphony.bdk.core.service_factory import ServiceFactory
from symphony.bdk.gen import ApiClient
from tests.utils.resource_utils import get_config_resource_filepath


@pytest.fixture(name="api_client_factory")
def fixture_api_client_factory():
    factory = MagicMock(ApiClientFactory)
    api_client = MagicMock(ApiClient)
    factory.get_pod_client.return_value = api_client
    factory.get_agent_client.return_value = api_client
    return factory


@pytest.fixture(name="config")
def fixture_config():
    config = BdkConfigLoader.load_from_file(get_config_resource_filepath("config.yaml"))
    return config


@pytest.fixture(name="service_factory")
def fixture_service_factory(api_client_factory, config):
    factory = ServiceFactory(api_client_factory, AuthSession(None), config)
    return factory


def test_get_user_service(service_factory):
    user_service = service_factory.get_user_service()
    assert user_service is not None
    assert isinstance(user_service, UserService)


def test_get_message_service(service_factory):
    message_service = service_factory.get_message_service()
    assert message_service is not None
    assert isinstance(message_service, MessageService)


def test_get_connection_service(service_factory):
    connection_service = service_factory.get_connection_service()
    assert connection_service is not None
    assert isinstance(connection_service, ConnectionService)


def test_get_stream_service(service_factory):
    stream_service = service_factory.get_stream_service()
    assert stream_service is not None
    assert isinstance(stream_service, StreamService)


def test_get_application_service(service_factory):
    application_service = service_factory.get_application_service()
    assert application_service is not None
    assert isinstance(application_service, ApplicationService)


def test_get_signal_service(service_factory):
    signal_service = service_factory.get_signal_service()
    assert signal_service is not None
    assert isinstance(signal_service, SignalService)


def test_get_datafeed_loop(config, service_factory):
    datafeed_loop = service_factory.get_datafeed_loop()
    assert datafeed_loop is not None
    assert isinstance(datafeed_loop, DatafeedLoopV1)

    config.datafeed.version = "v1"
    datafeed_loop = service_factory.get_datafeed_loop()
    assert datafeed_loop is not None
    assert isinstance(datafeed_loop, DatafeedLoopV1)

    config.datafeed.version = "something"
    datafeed_loop = service_factory.get_datafeed_loop()
    assert datafeed_loop is not None
    assert isinstance(datafeed_loop, DatafeedLoopV1)

    config.datafeed.version = "v2"
    datafeed_loop = service_factory.get_datafeed_loop()
    assert datafeed_loop is not None
    assert isinstance(datafeed_loop, DatafeedLoopV2)


def test_get_presence_service(service_factory):
    presence_service = service_factory.get_presence_service()
    assert presence_service is not None
    assert isinstance(presence_service, PresenceService)
