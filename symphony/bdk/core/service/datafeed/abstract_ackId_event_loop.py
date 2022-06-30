import logging
import time
from abc import abstractmethod, ABC

from symphony.bdk.core.auth.auth_session import AuthSession
from symphony.bdk.core.config.model.bdk_config import BdkConfig
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import AbstractDatafeedLoop
from symphony.bdk.core.service.datafeed.exception import EventError
from symphony.bdk.core.service.session.session_service import SessionService
from symphony.bdk.gen.agent_api.datafeed_api import DatafeedApi

EVENT_PROCESSING_MAX_DURATION_SECONDS = 30

logger = logging.getLogger(__name__)


class AbstractAckIdEventLoop(AbstractDatafeedLoop, ABC):
    """Base class for implementing datafeed types that relies on an ackId.
    """

    def __init__(self, datafeed_api: DatafeedApi, session_service: SessionService, auth_session: AuthSession,
                 config: BdkConfig):
        """

        :param datafeed_api: DatafeedApi to request the service
        :param session_service: the SessionService to get user session information
        :param auth_session: the AuthSession instance used to get session and key manager tokens
        :param config: the bot configuration
        """
        super().__init__(datafeed_api, session_service, auth_session, config)
        self._ack_id = ""

    async def _run_loop_iteration(self):
        events = await self._read_events()

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

    @abstractmethod
    async def _read_events(self):
        """Method called to read events"""
