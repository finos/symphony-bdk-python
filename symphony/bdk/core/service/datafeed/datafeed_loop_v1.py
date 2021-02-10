from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import AbstractDatafeedLoop
from symphony.bdk.core.service.datafeed.on_disk_datafeed_id_repository import OnDiskDatafeedIdRepository
from symphony.bdk.gen.exceptions import ApiException


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

    def __init__(self, datafeed_api, auth_session, config, repository=None):
        super().__init__(datafeed_api, auth_session, config)
        self.datafeed_repository = OnDiskDatafeedIdRepository(config) if repository is None else repository
        self.datafeed_id = None
        self.started = False

    async def start(self):
        self.datafeed_id = self.datafeed_repository.read()
        if not self.datafeed_id:
            self.datafeed_id = await self._create_datafeed_and_persist()
        self.started = True
        while self.started:
            try:
                await self._read_datafeed()
            except ApiException as e:
                if e.status == 400:
                    self.datafeed_id = await self._create_datafeed_and_persist()
                else:
                    raise e

    async def stop(self):
        self.started = False

    async def _read_datafeed(self):
        session_token = await self.auth_session.session_token
        key_manager_token = await self.auth_session.key_manager_token
        events = await self.datafeed_api.v4_datafeed_id_read_get(id=self.datafeed_id,
                                                                 session_token=session_token,
                                                                 key_manager_token=key_manager_token)
        if events is not None and events.value:
            await self.handle_v4_event_list(events.value)

    async def _create_datafeed_and_persist(self):
        session_token = await self.auth_session.session_token
        key_manager_token = await self.auth_session.key_manager_token
        response = await self.datafeed_api.v4_datafeed_create_post(session_token=session_token,
                                                                   key_manager_token=key_manager_token)
        datafeed_id = response.id
        self.datafeed_repository.write(response.id)
        return datafeed_id
