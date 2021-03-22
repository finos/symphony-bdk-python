from symphony.bdk.core.service.datafeed.abstract_datafeed_loop import AbstractDatafeedLoop
from symphony.bdk.core.service.datafeed.on_disk_datafeed_id_repository import OnDiskDatafeedIdRepository


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
        self._datafeed_repository = OnDiskDatafeedIdRepository(config) if repository is None else repository
        self._datafeed_id = None

    async def prepare_datafeed(self):
        self._datafeed_id = self._datafeed_repository.read()
        if not self._datafeed_id:
            await self.recreate_datafeed()

    async def read_datafeed(self):
        session_token = await self.auth_session.session_token
        key_manager_token = await self.auth_session.key_manager_token
        events = await self.datafeed_api.v4_datafeed_id_read_get(id=self._datafeed_id,
                                                                 session_token=session_token,
                                                                 key_manager_token=key_manager_token)
        if events is not None and events.value:
            return events.value

    async def recreate_datafeed(self):
        session_token = await self.auth_session.session_token
        key_manager_token = await self.auth_session.key_manager_token
        response = await self.datafeed_api.v4_datafeed_create_post(session_token=session_token,
                                                                   key_manager_token=key_manager_token)
        datafeed_id = response.id
        self._datafeed_repository.write(datafeed_id)
        self._datafeed_id = datafeed_id
