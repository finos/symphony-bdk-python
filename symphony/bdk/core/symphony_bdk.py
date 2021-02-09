from symphony.bdk.core.auth.auth_session import AuthSession, OboAuthSession
from symphony.bdk.core.auth.authenticator_factory import AuthenticatorFactory
from symphony.bdk.core.auth.exception import AuthInitializationException
from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.config.exception import BotNotConfiguredException
from symphony.bdk.core.service.connection.connection_service import ConnectionService
from symphony.bdk.core.service.datafeed.datafeed_loop_v1 import DatafeedLoopV1
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.service.user.user_service import UserService
from symphony.bdk.core.service_factory import ServiceFactory


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
        self._bot_session = AuthSession(self._authenticator_factory.get_bot_authenticator())

        self._service_factory = ServiceFactory(self._api_client_factory, self._bot_session, self._config)
        self._user_service = self._service_factory.get_user_service()
        self._message_service = self._service_factory.get_message_service()
        self._connection_service = self._service_factory.get_connection_service()
        if self._config.is_bot_configured():
            self._datafeed_loop = self._service_factory.get_datafeed_loop()
        else:
            raise BotNotConfiguredException()

    def bot_session(self) -> AuthSession:
        """Get the Bot authentication session. If the bot is not authenticated yet, perform the authentication for a new
        session.

        :return: The bot authentication session.
        """
        return self._bot_session

    def obo(self, user_id: int = None, username: str = None) -> OboAuthSession:
        """
        Get the Obo authentication session.

        :return: The obo authentication session
        """
        if user_id is not None:
            return self._authenticator_factory.get_obo_authenticator().authenticate_by_user_id(user_id)
        if username is not None:
            return self._authenticator_factory.get_obo_authenticator().authenticate_by_username(username)
        raise AuthInitializationException("At least user_id or username should be given to OBO authenticate the "
                                          "extension app")

    def messages(self) -> MessageService:
        """Get the MessageService from the BDK entry point.

        :return: The MessageService instance.

        """
        return self._message_service

    def datafeed(self) -> DatafeedLoopV1:
        """Get the Datafeed loop from the BDK entry point.

        :return: The Datafeed Loop instance.

        """
        return self._datafeed_loop

    def users(self) -> UserService:
        """Get the UserService from the BDK entry point.

        :return: The UserService instance.

        """
        return self._user_service

    def connections(self) -> ConnectionService:
        """Get the ConnectionService from the BDK entry point.

        :return: The ConnectionService instance.

        """
        return self._connection_service

    async def close_clients(self):
        """Close all the existing api clients created by the api client factory.
        """
        await self._api_client_factory.close_clients()
