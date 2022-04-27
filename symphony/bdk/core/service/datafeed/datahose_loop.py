import logging

from symphony.bdk.core.service.datafeed.abstract_ackId_event_loop import AbstractAckIdEventLoop
from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.gen.agent_model.v5_events_read_body import V5EventsReadBody

# DFv2 API authorizes a maximum length for the tag parameter
DATAHOSE_TAG_MAX_LENGTH = 80
TAG_DEFAULT_PREFIX = "datahose-"
TYPE = "datahose"

logger = logging.getLogger(__name__)


class DatahoseLoop(AbstractAckIdEventLoop):

    async def _prepare_datafeed(self):
        pass

    def __init__(self, datafeed_api: DatafeedApi, session_service: SessionService, auth_session: AuthSession,
                 config: BdkConfig):
        super().__init__(datafeed_api, session_service, auth_session, config)
        if config.datahose is not None:
            not_truncated_tag = \
                config.datahose.tag if config.datahose.tag is not None else TAG_DEFAULT_PREFIX + config.bot.username
            self._tag = not_truncated_tag[:DATAHOSE_TAG_MAX_LENGTH]
            self._retry = config.datahose.retry
            self._filters = config.datahose.filters

    async def _read_events(self):
        params = {
            "session_token": await self._auth_session.session_token,
            "key_manager_token": await self._auth_session.key_manager_token,
            "body": V5EventsReadBody(type=TYPE, tag=self._tag, filters=self._filters, ack_id=self._ack_id)
        }

        return await self._datafeed_api.read_events(**params)
