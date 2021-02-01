from symphony.bdk.core.datafeed.abstract_datafeed_loop import AbstractDatafeedLoop
from symphony.bdk.core.datafeed.on_disk_datafeed_id_repository import OnDiskDatafeedIdRepository
from symphony.bdk.gen.exceptions import ApiException


class DatafeedLoopV1(AbstractDatafeedLoop):

    def __init__(self, datafeed_api, auth_session, config, repository=None):
        super().__init__(datafeed_api, auth_session, config)
        self.datafeed_repository = OnDiskDatafeedIdRepository(config) if repository is None else repository
        self.datafeed_id = self.retrieve_datafeed()
        self.started = False

    async def start(self):
        try:
            if self.datafeed_id == "":
                self.datafeed_id = await self.create_datafeed_and_persist()
            self.started = True
            while self.started:  # I would like to know why do we use a do while in the java bdk for the read datafeed ?
                await self.read_datafeed()
        except ApiException:
            try:
                self.datafeed_id = await self.create_datafeed_and_persist()
            except ApiException:
                raise

    def stop(self):
        self.started = False

    async def read_datafeed(self):
        events = await self.datafeed_api.v4_datafeed_id_read_get(self.datafeed_id,
                                                                 self.auth_session.session_token,
                                                                 self.auth_session.key_manager_token)
        if events is not None and not (events.value == []):  # need to check if the call ever return None
            self.handle_v4_event_list(events.value)

    def retrieve_datafeed(self):
        return self.datafeed_repository.read()

    async def create_datafeed_and_persist(self):
        params = {
            'session_token': self.auth_session.session_token,
            'key_manager_token': self.auth_session.key_manager_token,
        }
        response = await self.datafeed_api.v4_datafeed_create_post(**params)
        datafeed_id = response.id
        self.datafeed_repository.write(response.id)
        return datafeed_id
