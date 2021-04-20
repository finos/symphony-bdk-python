"""Service factory module"""
from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.client.api_client_factory import ApiClientFactory
from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.service.application.application_service import ApplicationService
from symphony.bdk.core.service.connection.connection_service import ConnectionService, OboConnectionService
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import DatafeedVersion, AbstractDatafeedLoop
from symphony.bdk.core.service.datafeed.datafeed_loop_v1 import DatafeedLoopV1
from symphony.bdk.core.service.datafeed.datafeed_loop_v2 import DatafeedLoopV2
from symphony.bdk.core.service.health.health_service import HealthService
from symphony.bdk.core.service.message.message_service import MessageService, OboMessageService
from symphony.bdk.core.service.message.multi_attachments_messages_api import MultiAttachmentsMessagesApi
from symphony.bdk.core.service.presence.presence_service import PresenceService, OboPresenceService
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.core.service.signal.signal_service import SignalService, OboSignalService
from symphony.bdk.core.service.stream.stream_service import StreamService, OboStreamService
from symphony.bdk.core.service.user.user_service import UserService, OboUserService
from symphony.bdk.gen.agent_api.attachments_api import AttachmentsApi
from symphony.bdk.gen.agent_api.audit_trail_api import AuditTrailApi
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.gen.agent_api.share_api import ShareApi
from symphony.bdk.gen.agent_api.signals_api import SignalsApi
from symphony.bdk.gen.agent_api.system_api import SystemApi as AgentSystemApi
from symphony.bdk.gen.pod_api.app_entitlement_api import AppEntitlementApi
from symphony.bdk.gen.pod_api.application_api import ApplicationApi
from symphony.bdk.gen.pod_api.connection_api import ConnectionApi
from symphony.bdk.gen.pod_api.default_api import DefaultApi
from symphony.bdk.gen.pod_api.message_api import MessageApi
from symphony.bdk.gen.pod_api.message_suppression_api import MessageSuppressionApi
from symphony.bdk.gen.pod_api.pod_api import PodApi
from symphony.bdk.gen.pod_api.presence_api import PresenceApi
from symphony.bdk.gen.pod_api.room_membership_api import RoomMembershipApi
from symphony.bdk.gen.pod_api.session_api import SessionApi
from symphony.bdk.gen.pod_api.streams_api import StreamsApi
from symphony.bdk.gen.pod_api.system_api import SystemApi as PodSystemApi
from symphony.bdk.gen.pod_api.user_api import UserApi
from symphony.bdk.gen.pod_api.users_api import UsersApi


class ServiceFactory:
    """Factory responsible for creating BDK service instances for Symphony Bdk entry point:

    * User Service
    * Message Service
    * Connection Service
    * Stream Service
    * Datafeed Loop
    * ...
    """

    def __init__(
            self,
            api_client_factory: ApiClientFactory,
            auth_session: AuthSession,
            config: BdkConfig
    ):
        self._pod_client = api_client_factory.get_pod_client()
        self._agent_client = api_client_factory.get_agent_client()
        self._auth_session = auth_session
        self._config = config

    def get_user_service(self) -> UserService:
        """Returns a fully initialized UserService

        :return: a new UserService instance.
        """
        return UserService(
            UserApi(self._pod_client),
            UsersApi(self._pod_client),
            AuditTrailApi(self._agent_client),
            PodSystemApi(self._pod_client),
            self._auth_session
        )

    def get_message_service(self) -> MessageService:
        """Returns a fully initialized MessageService

        :return: a new MessageService instance.
        """
        return MessageService(
            MultiAttachmentsMessagesApi(self._agent_client),
            MessageApi(self._pod_client),
            MessageSuppressionApi(self._pod_client),
            StreamsApi(self._pod_client),
            PodApi(self._pod_client),
            AttachmentsApi(self._agent_client),
            DefaultApi(self._pod_client),
            self._auth_session
        )

    def get_connection_service(self) -> ConnectionService:
        """Returns a fully initialized ConnectionService

        :return: a new ConnectionService instance.
        """
        return ConnectionService(
            ConnectionApi(self._pod_client),
            self._auth_session
        )

    def get_stream_service(self) -> StreamService:
        """Returns a fully initialized StreamService

        :return: a new StreamService instance
        """
        return StreamService(
            StreamsApi(self._pod_client),
            RoomMembershipApi(self._pod_client),
            ShareApi(self._agent_client),
            self._auth_session)

    def get_application_service(self) -> ApplicationService:
        """Returns a fully initialized ApplicationService

        :return: a new ApplicationService instance
        """
        return ApplicationService(
            ApplicationApi(self._pod_client),
            AppEntitlementApi(self._pod_client),
            self._auth_session
        )

    def get_signal_service(self) -> SignalService:
        """Returns a fully initialized SignalService

        :return: a new SignalService instance
        """
        return SignalService(
            SignalsApi(self._agent_client),
            self._auth_session
        )

    def get_session_service(self) -> SessionService:
        """Returns a fully initialized SessionService

        :return: a new SessionService instance
        """
        return SessionService(
            SessionApi(self._pod_client),
            self._auth_session
        )

    def get_datafeed_loop(self) -> AbstractDatafeedLoop:
        """Returns a fully initialized DatafeedLoop

        :return: a new DatafeedLoop instance.
        """
        df_version = self._config.datafeed.version
        if df_version.lower() == DatafeedVersion.V2.value.lower():
            return DatafeedLoopV2(
                DatafeedApi(self._agent_client),
                self._auth_session,
                self._config
            )
        return DatafeedLoopV1(
            DatafeedApi(self._agent_client),
            self._auth_session,
            self._config
        )

    def get_health_service(self) -> HealthService:
        """Returns a fully initialized HealthService

        :return: a new HealthService instance
        """
        return HealthService(
            AgentSystemApi(self._agent_client),
            SignalsApi(self._agent_client)
        )

    def get_presence_service(self) -> PresenceService:
        """Returns a fully initialized PresenceService

        :return: a new PresenceService instance
        """
        return PresenceService(
            PresenceApi(self._pod_client),
            self._auth_session
        )


class OboServiceFactory:
    """Factory responsible for creating BDK service instances for OBO-enabled endpoints only:

    * User Service
    * Message Service
    * Connection Service
    * Stream Service

    See: `OBO-enabled endpoints <https://developers.symphony.com/restapi/reference#obo-enabled-endpoints>`_
    """

    def __init__(
            self,
            api_client_factory: ApiClientFactory,
            auth_session: AuthSession,
            config: BdkConfig
    ):
        self._pod_client = api_client_factory.get_pod_client()
        self._agent_client = api_client_factory.get_agent_client()
        self._auth_session = auth_session
        self._config = config

    def get_user_service(self) -> OboUserService:
        """Returns a fully initialized OboUserService

        :return: a new OboUserService instance.
        """
        return OboUserService(
            UserApi(self._pod_client),
            UsersApi(self._pod_client),
            self._auth_session
        )

    def get_message_service(self) -> OboMessageService:
        """Returns a fully initialized OboMessageService

        :return: a new OboMessageService instance.
        """
        return OboMessageService(
            MultiAttachmentsMessagesApi(self._agent_client),
            self._auth_session,
            MessageSuppressionApi(self._pod_client)
        )

    def get_connection_service(self) -> OboConnectionService:
        """Returns a fully initialized OboConnectionService

        :return: a new OboConnectionService instance.
        """
        return OboConnectionService(
            ConnectionApi(self._pod_client),
            self._auth_session
        )

    def get_stream_service(self) -> OboStreamService:
        """Returns a fully initialized OboStreamService

        :return: a new OboStreamService instance
        """
        return OboStreamService(
            StreamsApi(self._pod_client),
            RoomMembershipApi(self._pod_client),
            ShareApi(self._agent_client),
            self._auth_session)

    def get_presence_service(self) -> OboPresenceService:
        """Returns a fully initialized OboPresenceService

        :return: a new OboPresenceService instance
        """
        return OboPresenceService(
            PresenceApi(self._pod_client),
            self._auth_session
        )

    def get_signal_service(self) -> OboSignalService:
        """Returns a fully initialized OboSignalService

        :return: a new OboSignalService instance
        """
        return OboSignalService(
            SignalsApi(self._agent_client),
            self._auth_session
        )
