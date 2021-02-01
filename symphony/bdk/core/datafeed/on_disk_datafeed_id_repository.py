from abc import ABC, abstractmethod
from pathlib import Path
from symphony.bdk.core.config.model.bdk_config import BdkConfig


class DatafeedIdRepository(ABC):
    """A repository interface for storing a datafeed id
    By using the DatafeedLoopV1, the created datafeed id and agent base url should be persisted manually on the BDK side.
    """

    @abstractmethod
    def write(self, datafeed_id: str, agent_base_path: str):
        """Persists the created datafeed id into the storage.

        :param datafeed_id: the datafeed id to be persisted
        :param agent_base_path: the afent base path (i.e. scheme, host, port, context) to be persisted
        """
        pass

    @abstractmethod
    def read(self):
        """Reads the persisted datafeed from storage.

        :return the persisted datafeed id if present in storage, an empty string otherwise
        """
        pass

    @abstractmethod
    def read_agent_base_path(self):
        """Reads the persisted agent base path from the storage.

        :return: the persisted agent base path if present in storage, an empty string otherwise
        """
        pass


class OnDiskDatafeedIdRepository(DatafeedIdRepository):
    DATAFEED_ID_FILE = "datafeed.id"

    def __init__(self, config: BdkConfig):
        self.config = config

    def write(self, datafeed_id, agent_base_path=""):
        content = datafeed_id + "@" + agent_base_path
        try:
            self._get_datafeed_id_file().write_text(content, encoding='utf-8')
        except ValueError:
            raise ValueError("Error occurred when writing the datafeed Id")

    def read(self):
        content = self._read_datafeed_information()
        if content:
            datafeed_id = content.split("@")[0]
            return datafeed_id
        return ""

    def read_agent_base_path(self):
        content = self._read_datafeed_information()
        if content:
            agent_base_path = content.split("@")[1]
            return agent_base_path
        return ""

    def _read_datafeed_information(self):
        datafeed_id_path = self._get_datafeed_id_file()
        try:
            lines = datafeed_id_path.read_text(encoding='utf-8')
            first_line = lines.split("\n")[0]
            if "@" not in first_line:
                return ""
            return first_line
        except (OSError, IndexError) as e:
            print("No persisted datafeed id could be retrieved from disk", e)
            return ""

    def _get_datafeed_id_file(self) -> Path:
        filepath = self.config.datafeed.get_id_file_path()
        if filepath.is_dir():
            filepath = filepath / OnDiskDatafeedIdRepository.DATAFEED_ID_FILE
        return filepath
