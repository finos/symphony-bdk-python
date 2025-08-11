from symphony.bdk.core.auth.auth_session import OboAuthSession
from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.service.connection.connection_service import OboConnectionService
from symphony.bdk.core.service.message.message_service import OboMessageService
from symphony.bdk.core.service.signal.signal_service import OboSignalService
from symphony.bdk.core.service.stream.stream_service import OboStreamService
from symphony.bdk.core.service.user.user_service import OboUserService
from symphony.bdk.core.service_factory import OboServiceFactory


class OboServices:
    """Entry point for OBO-enabled services, see
    `the list of OBO-enabled endpoints <https://developers.symphony.com/restapi/reference/obo-enabled-endpoints#api-endpoints-enabled-for-obo>`_
    """

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_clients()

    def __init__(self, config: BdkConfig, obo_session: OboAuthSession):
        """

        :param config: the BDK configuration.
        :param obo_session: the OBO session to use.
        """
        self._config = config
        self._obo_session = obo_session

        self._api_client_factory = ApiClientFactory(config)
        self._service_factory = OboServiceFactory(
            self._api_client_factory, self._obo_session, self._config
        )
        self._connection_service = self._service_factory.get_connection_service()
        self._message_service = self._service_factory.get_message_service()
        self._stream_service = self._service_factory.get_stream_service()
        self._user_service = self._service_factory.get_user_service()
        self._signal_service = self._service_factory.get_signal_service()

    def connections(self) -> OboConnectionService:
        """

        :return: a fully initialized OboConnectionService instance.
        """
        return self._connection_service

    def messages(self) -> OboMessageService:
        """

        :return: a fully initialized OboMessageService instance.
        """
        return self._message_service

    def streams(self) -> OboStreamService:
        """

        :return: a fully initialized OboStreamService instance.
        """
        return self._stream_service

    def users(self) -> OboUserService:
        """

        :return: a fully initialized OboUserService instance.
        """
        return self._user_service

    def signals(self) -> OboSignalService:
        """

        :return: a fully initialized OboSignalService instance.
        """
        return self._signal_service

    async def close_clients(self):
        """Close all the existing api clients created by the api client factory."""
        await self._api_client_factory.close_clients()
