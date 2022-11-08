import logging

from symphony.bdk.core.retry import retry
from symphony.bdk.core.retry.strategy import read_datahose_retry
from symphony.bdk.core.service.datafeed.abstract_ackId_event_loop import AbstractAckIdEventLoop
from symphony.bdk.core.service.datafeed.abstract_datahose_loop import AbstractDatahoseLoop
from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.gen.agent_model.v5_events_read_body import V5EventsReadBody

# DFv2 API authorizes a maximum length for the tag parameter
DATAHOSE_TAG_MAX_LENGTH = 80
TYPE = "datahose"

logger = logging.getLogger(__name__)


class DatahoseLoop(AbstractAckIdEventLoop, AbstractDatahoseLoop):
    """A class for implementing the datahose loop service.

        This service will be started by calling :func:`~DatahoseLoop.start`.

        The BDK bot will listen to this datahose to get all the received real-time events that are set
        as event_types in the configuration.

        This service will be stopped by calling :func:`~DatahoseLoop.stop`
    """

    def __init__(self, datafeed_api: DatafeedApi, session_service: SessionService, auth_session: AuthSession,
                 config: BdkConfig):
        super().__init__(datafeed_api, session_service, auth_session, config)
        if config.datahose is not None:
            not_truncated_tag = config.datahose.tag if config.datahose.tag is not None \
                else TYPE + "-" + config.bot.username if config.bot.username is not None \
                else TYPE
            self._tag = not_truncated_tag[:DATAHOSE_TAG_MAX_LENGTH]
            self._retry = config.datahose.retry
            self._event_types = config.datahose.event_types

    async def start(self):
        if self._running:
            raise RuntimeError("The datahose service is already started")

        logger.debug("Starting datahose loop")

        self._bot_info = await self._session_service.get_session()
        try:
            await super().start()
        finally:
            logger.debug("Stopping datahose loop")

    @retry(retry=read_datahose_retry)
    async def _read_events(self):
        params = {
            "session_token": await self._auth_session.session_token,
            "key_manager_token": await self._auth_session.key_manager_token,
            "body": V5EventsReadBody(type=TYPE, tag=self._tag, event_types=self._event_types, ack_id=self._ack_id)
        }

        return await self._datafeed_api.read_events(**params)
