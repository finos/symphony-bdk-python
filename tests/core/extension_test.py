import pytest

from symphony.bdk.core.extension import ExtensionService

CONFIG = "config"
BOT_SESSION = "bot_session"
API_CLIENT_FACTORY = "api_client_factory"


class ExtensionType:
    pass


class ExtensionAware:
    def __init__(self, service=None):
        self._api_client_factory = None
        self._bot_session = None
        self._config = None
        self._service = service

    def set_api_client_factory(self, api_client_factory):
        self._api_client_factory = api_client_factory

    def set_bot_session(self, bot_session):
        self._bot_session = bot_session

    def set_config(self, config):
        self._config = config

    def get_service(self):
        return self._service


class WrongExtensionAware:
    def __init__(self):
        self._set_api_client_factory_called = False
        self._set_bot_session_called = False
        self._set_config_called = False

    def set_api_client_factory(self):
        self._set_api_client_factory_called = True

    def set_bot_session(self):
        self._set_bot_session_called = True

    def set_config(self):
        self._set_config_called = True


@pytest.fixture(name="extension_service")
def fixture_extension_service():
    return ExtensionService(API_CLIENT_FACTORY, BOT_SESSION, CONFIG)


def test_register_twice_the_same_extension_with_type(extension_service):
    extension_service.register(ExtensionType)

    with pytest.raises(ValueError):
        extension_service.register(ExtensionType)


def test_register_twice_the_same_extension_with_object(extension_service):
    extension_service.register(ExtensionType())

    with pytest.raises(ValueError):
        extension_service.register(ExtensionType())


def test_register_twice_the_same_extension_with_object_and_type(extension_service):
    extension_service.register(ExtensionType)

    with pytest.raises(ValueError):
        extension_service.register(ExtensionType())


def test_register_with_wrong_setters_definition_with_object(extension_service):
    extension_service.register(WrongExtensionAware())

    assert len(extension_service._extensions) == 1
    extension = extension_service._extensions[WrongExtensionAware]
    assert not extension._set_api_client_factory_called
    assert not extension._set_bot_session_called
    assert not extension._set_config_called


def test_register_with_wrong_setters_definition_with_type(extension_service):
    extension_service.register(WrongExtensionAware)

    assert len(extension_service._extensions) == 1
    extension = extension_service._extensions[WrongExtensionAware]
    assert not extension._set_api_client_factory_called
    assert not extension._set_bot_session_called
    assert not extension._set_config_called


def test_register_with_type(extension_service):
    extension_service.register(ExtensionAware)

    assert len(extension_service._extensions) == 1
    extension = extension_service._extensions[ExtensionAware]
    assert extension._api_client_factory == API_CLIENT_FACTORY
    assert extension._bot_session == BOT_SESSION
    assert extension._config == CONFIG


def test_register_with_object(extension_service):
    my_extension = ExtensionAware()

    extension_service.register(my_extension)
    assert len(extension_service._extensions) == 1
    extension = extension_service._extensions[ExtensionAware]
    assert my_extension == extension
    assert extension._api_client_factory == API_CLIENT_FACTORY
    assert extension._bot_session == BOT_SESSION
    assert extension._config == CONFIG


def test_service_when_extension_not_registered(extension_service):
    with pytest.raises(ValueError):
        extension_service.service(ExtensionType)


def test_service_when_extension_do_not_implement_get_service(extension_service):
    extension_service.register(ExtensionType)

    with pytest.raises(ValueError):
        extension_service.service(ExtensionType)


def test_service(extension_service):
    service = "service"
    extension_service.register(ExtensionAware(service))

    assert extension_service.service(ExtensionAware) == service
