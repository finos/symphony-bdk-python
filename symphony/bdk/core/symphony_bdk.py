from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.auth.authenticator_factory import AuthenticatorFactory
from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.auth.authenticator_factory import AuthenticatorFactory
from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.service.message.message_service import MessageService
from symphony.bdk.core.service.message.multi_attachments_messages_api import MultiAttachmentsMessagesApi
from symphony.bdk.gen.agent_api.attachments_api import AttachmentsApi
from symphony.bdk.gen.pod_api.default_api import DefaultApi
from symphony.bdk.gen.pod_api.message_api import MessageApi
from symphony.bdk.gen.pod_api.message_suppression_api import MessageSuppressionApi
from symphony.bdk.gen.pod_api.pod_api import PodApi
from symphony.bdk.gen.pod_api.streams_api import StreamsApi

from symphony.bdk.core.config.exception.bot_not_configured_exception import BotNotConfiguredException
from symphony.bdk.core.service.datafeed.datafeed_loop_v1 import DatafeedLoopV1
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi


class SymphonyBdk:
    """
    BDK entry point
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
        self._message_service = MessageService(
            MultiAttachmentsMessagesApi(self._agent_client),
            MessageApi(self._pod_client),
            MessageSuppressionApi(self._pod_client),
            StreamsApi(self._pod_client),
            PodApi(self._pod_client),
            AttachmentsApi(self._agent_client),
            DefaultApi(self._pod_client),
            self._bot_session
        )
        self._datafeed_loop = self.get_datafeed_loop()

    def bot_session(self) -> AuthSession:
        """
        Get the Bot authentication session. If the bot is not authenticated yet, perform the authentication for a new
        session.

        :return: The bot authentication session.
        """
        return self._bot_session

    def messages(self) -> MessageService:
        """
        Get the MessageService from the BDK entry point.

        :return: The MessageService instance.

        """
        return self._message_service

    def datafeed(self) -> DatafeedLoopV1:
        """Get the Datafeed loop from the BDK entry point.

        :return: The Datafeed Loop instance.

        """
        return self._datafeed_loop

    def get_datafeed_loop(self) -> DatafeedLoopV1:
        if self._config.is_bot_configured():
            return DatafeedLoopV1(DatafeedApi(self._agent_client), self._bot_session, self._config)
        else:
            raise BotNotConfiguredException()

    async def close_clients(self):
        """
        Close all the existing api clients created by the api client factory.
        """
        await self._api_client_factory.close_clients()
