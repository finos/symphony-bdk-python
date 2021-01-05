import logging
import os

DATAFEED_ID_FILE = 'datafeed.id'

log = logging.getLogger(__name__)


class OnDiskDatafeedIdRepository:
    def __init__(self, datafeed_id_folder):
        self.datafeed_id_file_path = self._get_datafeed_id_file_path(datafeed_id_folder)

    def read_datafeed_id_from_file(self):
        log.debug(f'Retrieving datafeed id from file {self.datafeed_id_file_path}')
        if os.path.exists(self.datafeed_id_file_path):
            with open(self.datafeed_id_file_path, 'r') as datafeed_id_file:
                line = datafeed_id_file.readline()
                if line:
                    index = line.find("@")
                    if index != -1:
                        datafeed_id = line[0:index]
                        log.debug(f'Retrieved datafeed id: {datafeed_id}')
                        return datafeed_id
        log.debug(f'Could not retrieve datafeed id from file {self.datafeed_id_file_path}')
        return None

    def store_datafeed_id_to_file(self, datafeed_id, agent_url):
        with open(self.datafeed_id_file_path, 'w') as datafeed_id_file:
            line = f'{datafeed_id}@{agent_url}'
            log.debug(f'Writing {line} to {self.datafeed_id_file_path}')
            datafeed_id_file.write(line)

    def _get_datafeed_id_file_path(self, datafeed_id_folder):
        datafeed_id_file_path = os.path.join(datafeed_id_folder, DATAFEED_ID_FILE)
        if os.path.exists(datafeed_id_file_path) and os.path.isdir(datafeed_id_file_path):
            datafeed_id_file_path = os.path.join(datafeed_id_file_path, DATAFEED_ID_FILE)
        return os.path.abspath(datafeed_id_file_path)
