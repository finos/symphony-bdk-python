import logging
import time
from typing import Optional

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.retry import retry
from symphony.bdk.core.retry.strategy import read_datafeed_retry
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import AbstractDatafeedLoop
from symphony.bdk.core.service.datafeed.exception import EventError
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi
from symphony.bdk.gen.agent_model.ack_id import AckId
from symphony.bdk.gen.agent_model.v5_datafeed import V5Datafeed
from symphony.bdk.gen.agent_model.v5_datafeed_create_body import V5DatafeedCreateBody

# Based on the DFv2 default visibility timeout, after which an event is re-queued
EVENT_PROCESSING_MAX_DURATION_SECONDS = 30

# DFv2 API authorizes a maximum length for the tag parameter
DATAFEED_TAG_MAX_LENGTH = 100

logger = logging.getLogger(__name__)


class DatafeedLoopV2(AbstractDatafeedLoop):
    """A class for implementing the datafeed v2 loop service.

        This service will be started by calling :func:`~DatafeedLoopV2.start`.

        On the very first run, the BDK bot will try to retrieve the list of datafeed to which it is listening.
        Since each bot should only listening to just one datafeed, the first datafeed in the list will be used by
        the bot to be listened to. If the retrieved list is empty, the BDK bot will create a new datafeed to listen.

        The BDK bot will listen to this datafeed to get all the received real-time events.

        If this datafeed becomes stale or faulty, the BDK bot will create the new one for listening.

        This service will be stopped by calling :func:`~DatafeedLoopV1.stop`

        If the datafeed service is stopped during a read datafeed call, it has to wait until the last read finish to be
        really stopped
        """

    def __init__(self, datafeed_api: DatafeedApi, session_service: SessionService, auth_session: AuthSession,
                 config: BdkConfig):
        super().__init__(datafeed_api, session_service, auth_session, config)
        self._ack_id = ""
        self._datafeed_id = None
        self._tag = config.bot.username[0:DATAFEED_TAG_MAX_LENGTH]

    async def _prepare_datafeed(self):
        datafeed = await self._retrieve_datafeed()
        if not datafeed:
            datafeed = await self._create_datafeed()
        self._datafeed_id = datafeed.id

    async def _run_loop_iteration(self):
        events = await self._read_datafeed()

        is_run_successful = await self._run_all_listener_tasks(events.events)
        if is_run_successful:
            # updates ack id so that on next call DFv2 knows that events have been processed
            # if not updated, events will be requeued after some time, typically 30s
            self._ack_id = events.ack_id

    async def _run_all_listener_tasks(self, events):
        start = time.time()
        done_tasks = await self._run_listener_tasks(events)
        elapsed = time.time() - start

        if elapsed > EVENT_PROCESSING_MAX_DURATION_SECONDS:
            logging.warning("Events processing took longer than %s seconds, "
                            "this might lead to events being re-queued in datafeed and re-dispatched. "
                            "You might want to consider processing the event in a separated asyncio task if needed.",
                            EVENT_PROCESSING_MAX_DURATION_SECONDS)

        return await self._are_tasks_successful(done_tasks)

    async def _are_tasks_successful(self, tasks):
        success = True
        for task in tasks:
            exception = task.exception()
            if exception:
                if isinstance(exception, EventError):
                    logger.warning("Failed to process events inside %s, "
                                   "will not update ack id, events will be re-queued",
                                   task.get_name(),
                                   exc_info=exception)
                    success = False
                else:
                    logging.debug("Exception occurred inside %s", task.get_name(), exc_info=exception)
        return success

    @retry(retry=read_datafeed_retry)
    async def _read_datafeed(self):
        params = {
            "session_token": await self._auth_session.session_token,
            "key_manager_token": await self._auth_session.key_manager_token,
            "datafeed_id": self._datafeed_id,
            "ack_id": AckId(ack_id=self._ack_id)
        }
        return await self._datafeed_api.read_datafeed(**params)

    async def recreate_datafeed(self):
        await self._delete_datafeed()
        datafeed = await self._create_datafeed()

        self._datafeed_id = datafeed.id
        self._ack_id = ""

    @retry
    async def _retrieve_datafeed(self) -> Optional[V5Datafeed]:
        session_token = await self._auth_session.session_token
        key_manager_token = await self._auth_session.key_manager_token
        datafeeds = await self._datafeed_api.list_datafeed(session_token=session_token,
                                                           key_manager_token=key_manager_token,
                                                           tag=self._tag)
        if datafeeds:
            return datafeeds[0]
        return None

    @retry
    async def _create_datafeed(self) -> V5Datafeed:
        session_token = await self._auth_session.session_token
        key_manager_token = await self._auth_session.key_manager_token

        return await self._datafeed_api.create_datafeed(session_token=session_token,
                                                        key_manager_token=key_manager_token,
                                                        body=V5DatafeedCreateBody(tag=self._tag))

    @retry
    async def _delete_datafeed(self) -> None:
        session_token = await self._auth_session.session_token
        key_manager_token = await self._auth_session.key_manager_token
        await self._datafeed_api.delete_datafeed(datafeed_id=self._datafeed_id,
                                                 session_token=session_token,
                                                 key_manager_token=key_manager_token)
