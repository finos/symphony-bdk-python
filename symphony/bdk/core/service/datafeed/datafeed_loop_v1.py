import logging

from symphony.bdk.core.retry import retry
from symphony.bdk.core.retry.strategy import read_datafeed_retry
from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import AbstractDatafeedLoop
from symphony.bdk.core.service.datafeed.exception import EventError
from symphony.bdk.core.service.datafeed.on_disk_datafeed_id_repository import OnDiskDatafeedIdRepository

logger = logging.getLogger(__name__)


class DatafeedLoopV1(AbstractDatafeedLoop):
    """A class for implementing the datafeed v1 loop service.

    This service will be started by calling :func:`~DatafeedLoopV1.start`.

    On the very first run, the datafeed will be created and the BDK bot will listen to this datafeed to receive
    real-time events. With datafeed service v1, we don't have the api endpoint to retrieve the datafeed id that a
    service account is listening to, so, the id of the created datafeed must be persisted in the bot side.

    The BDK bot will listen to this datafeed to get all the received real-time events.

    On another run, the bot will firstly retrieve the datafeed that was persisted and try to read the real-time
    events from this datafeed. If this datafeed is expired or faulty, the datafeed service will create the new one for
    listening.

    This service will be stopped by calling :func:`~DatafeedLoopV1.stop`

    If the datafeed service is stopped during a read datafeed call, it has to wait until the last read finish to be
    really stopped
    """

    def __init__(self, datafeed_api, session_service, auth_session, config, repository=None):
        super().__init__(datafeed_api, session_service, auth_session, config)
        self._datafeed_repository = OnDiskDatafeedIdRepository(config) if repository is None else repository
        self._datafeed_id = None

    async def start(self):
        if self._running:
            raise RuntimeError("The datafeed service V1 is already started")

        logger.debug("Starting datafeed V1 loop")

        self._bot_info = await self._session_service.get_session()
        await self._prepare_datafeed()
        try:
            await super().start()
        finally:
            logger.debug("Stopping datafeed loop")

    async def _prepare_datafeed(self):
        self._datafeed_id = self._datafeed_repository.read()
        if not self._datafeed_id:
            await self.recreate_datafeed()

    @retry
    async def recreate_datafeed(self):
        session_token = await self._auth_session.session_token
        key_manager_token = await self._auth_session.key_manager_token
        response = await self._datafeed_api.v4_datafeed_create_post(session_token=session_token,
                                                                    key_manager_token=key_manager_token)
        datafeed_id = response.id
        self._datafeed_repository.write(datafeed_id)
        self._datafeed_id = datafeed_id

    async def _run_loop_iteration(self):
        events = await self._read_datafeed()
        done_tasks = await self._run_listener_tasks(events)
        for future in done_tasks:
            await self._log_listener_exception(future)

    @retry(retry=read_datafeed_retry)
    async def _read_datafeed(self):
        session_token = await self._auth_session.session_token
        key_manager_token = await self._auth_session.key_manager_token
        events = await self._datafeed_api.v4_datafeed_id_read_get(id=self._datafeed_id,
                                                                  session_token=session_token,
                                                                  key_manager_token=key_manager_token)
        return events.value if events is not None and events.value else []

    async def _log_listener_exception(self, task):
        exception = task.exception()
        if exception:
            if isinstance(exception, EventError):
                logger.warning("EventError occurred inside %s. "
                               "EventError is not supported for DFv1, events will not get re-queued",
                               task.get_name(), exc_info=exception)
            else:
                logging.debug("Exception occurred inside %s", task.get_name(), exc_info=exception)
