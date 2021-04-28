from pathlib import Path

from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig

VERSION = "version"
DF_ID_FILE_PATH = "idFilePath"

DF_V1 = "v1"


class BdkDatafeedConfig:
    """Class holding datafeed specific configuration.
    """

    def __init__(self, config):
        """

        :param config: the dict containing the datafeed specific confguration.
        """
        self.version = DF_V1
        self.id_file_path = ""
        self.retry = BdkRetryConfig(dict(maxAttempts=BdkRetryConfig.INFINITE_MAX_ATTEMPTS))
        if config is not None:
            self.id_file_path = Path(config.get(DF_ID_FILE_PATH)) if DF_ID_FILE_PATH in config else ""
            self.version = config.get(VERSION)
            if "retry" in config:
                self.retry = BdkRetryConfig(config.get("retry"))

    def get_id_file_path(self) -> Path:
        """

        :return: a Path instance of the datafeed.id file where to persist the datafeed.id (applicable for DFv1 only)
        :rtype: Path
        """
        return self.id_file_path if self.id_file_path else Path(".")
