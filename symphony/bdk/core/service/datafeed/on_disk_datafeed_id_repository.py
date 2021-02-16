import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from symphony.bdk.core.config.model.bdk_config import BdkConfig

logger = logging.getLogger(__name__)


class DatafeedIdRepository(ABC):
    """A repository interface for storing a datafeed id.
    By using the DatafeedLoopV1, the created datafeed id and agent base url has to be persisted on the BDK side.
    """

    @abstractmethod
    def write(self, datafeed_id: str, agent_base_path: str):
        """Persists the created datafeed id into the storage.

        :param datafeed_id: the datafeed id to be persisted
        :param agent_base_path: the agent base path (i.e. scheme, host, port, context) to be persisted
        """

    @abstractmethod
    def read(self):
        """Reads the persisted datafeed from storage.

        :return the persisted datafeed id if present in storage, an empty string otherwise
        """


class OnDiskDatafeedIdRepository(DatafeedIdRepository):
    """Implementation of DatafeedIdRepository interface for persisting a datafeed id on disk."""
    DATAFEED_ID_FILE = "datafeed.id"

    def __init__(self, config: BdkConfig):
        self.config = config
        self.datafeed_id_file_path = self._get_datafeed_id_file()

    def write(self, datafeed_id, agent_base_path=""):
        self.datafeed_id_file_path.write_text(f"{datafeed_id}@{agent_base_path}")

    def read(self) -> str:
        logger.debug("Retrieving datafeed id from file %s", self.datafeed_id_file_path.absolute())
        if not os.path.exists(self.datafeed_id_file_path):
            logger.debug("Could not retrieve datafeed id from file %s: file not found",
                          self.datafeed_id_file_path.absolute())
            return None

        return self._read_in_file()

    def _read_in_file(self):
        with open(self.datafeed_id_file_path, "r") as datafeed_id_file:
            line = datafeed_id_file.readline()
            return self._read_in_line(line)

    def _read_in_line(self, line):
        index = line.find("@")
        if index == -1:
            logger.debug("Could not retrieve datafeed id from file %s: file without datafeed id information",
                          self.datafeed_id_file_path.absolute())
            return None
        datafeed_id = line[0:index]
        logger.debug("Retrieved datafeed id: %s", datafeed_id)
        return datafeed_id

    def _get_datafeed_id_file(self) -> Path:
        filepath = self.config.datafeed.get_id_file_path()
        if filepath.is_dir():
            filepath = filepath / OnDiskDatafeedIdRepository.DATAFEED_ID_FILE
        return filepath
