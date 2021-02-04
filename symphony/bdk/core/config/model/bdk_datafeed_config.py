from pathlib import Path

VERSION = "version"
DF_ID_FILE_PATH = "idFilePath"

DF_V1 = "v1"


class BdkDatafeedConfig:

    def __init__(self, config):
        self.id_file_path = ""
        self.version = DF_V1
        if config is not None:
            self.id_file_path = Path(config.get(DF_ID_FILE_PATH)) if DF_ID_FILE_PATH in config else ""

    def get_id_file_path(self):
        if self.id_file_path:
            return self.id_file_path
        else:
            return Path(".")
