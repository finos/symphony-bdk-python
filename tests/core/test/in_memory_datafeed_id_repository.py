from symphony.bdk.core.service.datafeed.on_disk_datafeed_id_repository import DatafeedIdRepository


class InMemoryDatafeedIdRepository(DatafeedIdRepository):
    def __init__(self, default_agent_base_path: str):
        self.default_agent_base_path = default_agent_base_path
        self.datafeed_id = None
        self.agent_base_path = None

    def write(self, datafeed_id: str, agent_base_path=None):
        self.datafeed_id = datafeed_id
        self.agent_base_path = self.default_agent_base_path if agent_base_path is None else agent_base_path

    def read(self):
        return "" if self.datafeed_id is None else self.datafeed_id

    def read_agent_base_path(self):
        return "" if self.agent_base_path is None else self.agent_base_path
