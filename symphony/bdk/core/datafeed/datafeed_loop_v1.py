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
        if self.datafeed_id == "":
            self.datafeed_id = await self.__create_datafeed_and_persist()
        self.started = True
        while self.started:
            try:
                await self.__read_datafeed()
            except ApiException:
                try:
                    self.datafeed_id = await self.__create_datafeed_and_persist()
                except ApiException:
                    raise

    def stop(self):
        self.started = False

    async def __read_datafeed(self):
        events = await self.datafeed_api.v4_datafeed_id_read_get(id=self.datafeed_id,
                                                                 session_token=self.auth_session.session_token,
                                                                 key_manager_token=self.auth_session.key_manager_token)
        if events is not None and not (events.value == []):  # need to check if the call ever return None
            self.handle_v4_event_list(events.value)

    async def __create_datafeed_and_persist(self):
        response = await self.datafeed_api.v4_datafeed_create_post(session_token=self.auth_session.session_token,
                                                                   key_manager_token=self.auth_session.key_manager_token)
        datafeed_id = response.id
        self.datafeed_repository.write(response.id)
        return datafeed_id

    def retrieve_datafeed(self):
        return self.datafeed_repository.read()
