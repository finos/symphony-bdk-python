"""Module for managing extensions.
"""
import logging
from abc import ABC, abstractmethod
from typing import Union

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.config.model.bdk_config import BdkConfig

logger = logging.getLogger(__name__)


class BdkConfigAware(ABC):
    """Interface that extensions need to implement to have the config injected
    """
    @abstractmethod
    def set_config(self, bdk_config: BdkConfig):
        """Method that is called by the :class:`ExtensionService` to inject the BDK configuration.

        :param bdk_config: the BDK configuration
        :return: None
        """


class BdkAuthenticationAware(ABC):
    """Interface that extensions need to implement to have the bot session injected
    """
    @abstractmethod
    def set_bot_session(self, auth_session: AuthSession):
        """Method that is called by the :class:`ExtensionService` to inject the BDK auth session.

        :param auth_session: the BDK auth session
        :return: None
        """


class BdkApiClientFactoryAware(ABC):
    """Interface that extensions need to implement to have the api client factory injected
    """
    @abstractmethod
    def set_api_client_factory(self, api_client_factory: ApiClientFactory):
        """Method that is called by the :class:`ExtensionService` to inject the BDK api client factory.

        :param api_client_factory: the BDK api client factory
        :return: None
        """


class BdkExtensionServiceProvider(ABC):
    """Interface that extensions need to implement to expose a service
    """
    @abstractmethod
    def get_service(self):
        """Method that is called by the :func:`~ExtensionService.service`

        :return: a service
        """


class ExtensionService:
    """Service class for managing extensions
    """
    def __init__(self, api_client_factory, bot_session, config):
        self._api_client_factory = api_client_factory
        self._bot_session = bot_session
        self._config = config
        self._extensions = {}

    def register(self, extension_type_or_instance: Union[type, object]):
        """Registers and instantiates an extension.

        :param extension_type_or_instance: Type of the extension or extension instance
        :raise: ValueError if the extension is already registered
        :return: None
        """
        if isinstance(extension_type_or_instance, type):
            extension = extension_type_or_instance()
            extension_type = extension_type_or_instance
        else:
            extension = extension_type_or_instance
            extension_type = type(extension_type_or_instance)

        if extension_type in self._extensions:
            raise ValueError(f"Extension {str(extension_type)} already registered")
        self._extensions[extension_type] = extension

        self._inject_api_client_factory(extension)
        self._inject_bot_session(extension)
        self._inject_config(extension)

    def service(self, extension_type: type):
        """Retrieves an extension service instance

        :param extension_type: Type of the extension
        :raise: ValueError if the extension does not implement a get_service method
        :return: the service instance
        """
        if extension_type not in self._extensions:
            raise ValueError(f"Extension {str(extension_type)} not registered")
        extension = self._extensions[extension_type]
        try:
            return extension.get_service()
        except AttributeError:
            raise ValueError(f"Extension {str(extension_type)} does not implement the get_service method")

    def _inject_api_client_factory(self, extension):
        try:
            extension.set_api_client_factory(self._api_client_factory)
        except AttributeError:
            logger.debug("Extension is not api client aware")
        except TypeError:
            logger.warning("set_api_client_factory method must have a single positional argument")

    def _inject_bot_session(self, extension):
        try:
            extension.set_bot_session(self._bot_session)
        except AttributeError:
            logger.debug("Extension is not authentication aware")
        except TypeError:
            logger.warning("set_bot_session method must have a single positional argument")

    def _inject_config(self, extension):
        try:
            extension.set_config(self._config)
        except AttributeError:
            logger.debug("Extension is not configuration aware")
        except TypeError:
            logger.warning("set_configuration method must have a single positional argument")
