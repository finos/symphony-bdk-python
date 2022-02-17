import logging
from abc import ABC, abstractmethod

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.model.bdk_config import BdkConfig

logger = logging.getLogger(__name__)

_RETRY_CONFIG_AWARE = []


def retry_aware(cls):
    _RETRY_CONFIG_AWARE.append(cls)
    return cls


class BdkConfigAware(ABC):
    @abstractmethod
    def set_configuration(self, bdk_config: BdkConfig):
        pass


class BdkAuthenticationAware(ABC):
    @abstractmethod
    def set_auth_session(self, auth_session: AuthSession):
        pass


class BdkRetryConfigAware(ABC):
    """Marker interface to set attribute self,_retry_config used by @retry decorator.
    """


class ExtensionService:
    def __init__(self, bot_session: AuthSession, bdk_config: BdkConfig):
        self._bot_session = bot_session
        self._bdk_config = bdk_config
        self._extensions = {}
        # what do we do if no bot configured (OBO-only usecase)?

    def register(self, extension_type: type):
        if extension_type in self._extensions:
            raise ValueError(f"Extension {extension_type} already registered")
        extension = extension_type.__new__(extension_type)
        self._extensions[extension_type] = extension

        if isinstance(extension, BdkRetryConfigAware) or extension_type in _RETRY_CONFIG_AWARE:
            setattr(extension, "_retry_config", self._bdk_config.retry)

        try:
            extension.set_configuration(self._bdk_config)
        except AttributeError:
            logging.debug("Extension is not a configuration aware")
        except TypeError:
            logging.warning("set_configuration method must have a single positional argument")

        try:
            extension.set_auth_session(self._bot_session)
        except AttributeError:
            logging.debug("Extension is not a authentication aware")
        except TypeError:
            logging.warning("set_auth_session method must have a single positional argument")

    def get_service(self, extension_type):
        extension = self._extensions[extension_type]
        if extension is None:
            raise ValueError(f"Extension {extension_type} not defined")

        return extension.get_service()  # will raise an AttributeError or TypeError if get_service() not defined
