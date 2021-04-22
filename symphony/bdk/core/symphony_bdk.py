"""Module containing SymphonyBdk class which acts as en entry point for all BDK services.
"""
import functools
import logging

from symphony.bdk.core.activity.registry import ActivityRegistry
from symphony.bdk.core.auth.auth_session import AuthSession, OboAuthSession
from symphony.bdk.core.auth.authenticator_factory import AuthenticatorFactory
from symphony.bdk.core.auth.exception import AuthInitializationError
from symphony.bdk.core.auth.ext_app_authenticator import ExtensionAppAuthenticator
from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.config.exception import BotNotConfiguredError
from symphony.bdk.core.service.application.application_service import ApplicationService
from symphony.bdk.core.service.connection.connection_service import ConnectionService
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import AbstractDatafeedLoop
from symphony.bdk.core.service.health.health_service import HealthService
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.service.obo_services import OboServices
from symphony.bdk.core.service.presence.presence_service import PresenceService
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.core.service.signal.signal_service import SignalService
from symphony.bdk.core.service.stream.stream_service import StreamService
from symphony.bdk.core.service.user.user_service import UserService
from symphony.bdk.core.service_factory import ServiceFactory

logger = logging.getLogger(__name__)


def bot_service(func):
    """Decorator to check if a bot service account is configured before making the actual function call.

    :param func: the decorated function.
    :return: the value returned by the decorated function with the passed arguments.
    :raise: BotNotConfiguredError if the bit service account is not configured.
    """

    @functools.wraps(func)
    def check_if_bot_configured_and_call_function(*args):
        symphony_bdk = args[0]
        if not symphony_bdk._config.bot.is_authentication_configured():
            raise BotNotConfiguredError("Error calling bot service ")
        return func(*args)

    return check_if_bot_configured_and_call_function


class SymphonyBdk:
    """BDK entry point
    """

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_clients()

    def __init__(self, config):
        self._config = config
        self._api_client_factory = ApiClientFactory(config)
        self._pod_client = self._api_client_factory.get_pod_client()
        self._agent_client = self._api_client_factory.get_agent_client()
        self._authenticator_factory = AuthenticatorFactory(config, api_client_factory=self._api_client_factory)

        self._bot_session = None
        self._ext_app_authenticator = None
        self._service_factory = None
        self._user_service = None
        self._message_service = None
        self._connection_service = None
        self._stream_service = None
        self._application_service = None
        self._signal_service = None
        self._session_service = None
        self._datafeed_loop = None
        self._health_service = None
        self._presence_service = None
        self._activity_registry = None

        if self._config.bot.is_authentication_configured():
            self._initialize_bot_services()
        else:
            logging.info("Bot (service account) credentials have not been configured."
                         "You can however use services in OBO mode if app authentication is configured.")

    def _initialize_bot_services(self):
        self._bot_session = AuthSession(self._authenticator_factory.get_bot_authenticator())
        self._service_factory = ServiceFactory(self._api_client_factory, self._bot_session, self._config)
        self._user_service = self._service_factory.get_user_service()
        self._message_service = self._service_factory.get_message_service()
        self._connection_service = self._service_factory.get_connection_service()
        self._stream_service = self._service_factory.get_stream_service()
        self._application_service = self._service_factory.get_application_service()
        self._signal_service = self._service_factory.get_signal_service()
        self._session_service = self._service_factory.get_session_service()
        self._datafeed_loop = self._service_factory.get_datafeed_loop()
        self._health_service = self._service_factory.get_health_service()
        self._presence_service = self._service_factory.get_presence_service()
        # creates ActivityRegistry that subscribes to DF Loop events
        self._activity_registry = ActivityRegistry(self._session_service)
        self._datafeed_loop.subscribe(self._activity_registry)

    @bot_service
    def bot_session(self) -> AuthSession:
        """Get the Bot authentication session. If the bot is not authenticated yet, perform the authentication for a new
        session.

        :return: The bot authentication session.
        """
        return self._bot_session

    def app_authenticator(self) -> ExtensionAppAuthenticator:
        """Get the extension app authenticator.

        :return: a new instance of :class:`symphony.bdk.core.auth.ext_app_authenticator.ExtensionAppAuthenticator`
        """
        if self._ext_app_authenticator is None:
            self._ext_app_authenticator = self._authenticator_factory.get_extension_app_authenticator()
        return self._ext_app_authenticator

    def obo(self, user_id: int = None, username: str = None) -> OboAuthSession:
        """Get the Obo authentication session.

        :return: The obo authentication session
        """
        if user_id is not None:
            return self._authenticator_factory.get_obo_authenticator().authenticate_by_user_id(user_id)
        if username is not None:
            return self._authenticator_factory.get_obo_authenticator().authenticate_by_username(username)
        raise AuthInitializationError("At least user_id or username should be given to OBO authenticate the "
                                      "extension app")

    def obo_services(self, obo_session: OboAuthSession) -> OboServices:
        """Return the entry point of all OBO-enabled services and endpoints.

        :param obo_session: the obo_session to use.
        :return: a new OboServices instance.
        """
        return OboServices(self._config, obo_session)

    @bot_service
    def messages(self) -> MessageService:
        """Get the MessageService from the BDK entry point.

        :return: The MessageService instance.
        """
        return self._message_service

    @bot_service
    def streams(self) -> StreamService:
        """Get the StreamService from the BDK entry point.

        :return: The StreamService instance.
        """
        return self._stream_service

    @bot_service
    def datafeed(self) -> AbstractDatafeedLoop:
        """Get the Datafeed loop from the BDK entry point.

        :return: The Datafeed Loop instance.
        """
        return self._datafeed_loop

    @bot_service
    def users(self) -> UserService:
        """Get the UserService from the BDK entry point.

        :return: The UserService instance.
        """
        return self._user_service

    @bot_service
    def connections(self) -> ConnectionService:
        """Get the ConnectionService from the BDK entry point.

        :return: The ConnectionService instance.
        """
        return self._connection_service

    @bot_service
    def applications(self) -> ApplicationService:
        """Get the ApplicationService from the BDK entry point.

        :return: The ApplicationService instance.
        """
        return self._application_service

    @bot_service
    def signals(self) -> SignalService:
        """Get the SignalService from the BDK entry point.

        :return: The SignalService instance.
        """
        return self._signal_service

    @bot_service
    def sessions(self) -> SessionService:
        """Get the SessionService from the BDK entry point.

        :return: The SessionService instance.
        """
        return self._session_service

    @bot_service
    def health(self) -> HealthService:
        """Get the HealthService from the BDK entry point.

        :return: The HealthService instance.
        """
        return self._health_service

    @bot_service
    def presence(self) -> PresenceService:
        """Get the PresenceService from the BDK entry point.

        :return: The PresenceService instance.
        """
        return self._presence_service

    @bot_service
    def activities(self) -> ActivityRegistry:
        """Get the :class:`ActivityRegistry` from the BDK entry point.

        :return: The :class:`ActivityRegistry` instance.

        """
        return self._activity_registry

    async def close_clients(self):
        """Close all the existing api clients created by the api client factory.
        """
        await self._api_client_factory.close_clients()
