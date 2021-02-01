from pathlib import Path


class BdkDatafeedConfig:

    def __init__(self, config):
        self.id_file_path = ""
        self.version = "v1"
        if config is not None:
            self.id_file_path = config.get("idFilePath") if "idFilePath" in config else ""
            self.version = config.get("version") if "version" in config else "v1"

    def get_id_file_path(self):
        if self.id_file_path:
            return self.id_file_path
        else:
            return Path(".")

