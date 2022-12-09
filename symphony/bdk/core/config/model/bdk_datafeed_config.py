import logging
from pathlib import Path

from symphony.bdk.core.config.model.bdk_retry_config import BdkRetryConfig

VERSION = "version"
DF_ID_FILE_PATH = "idFilePath"
DF_V1 = "v1"
DF_V2 = "v2"


def log_dfv1_deprecation(version):
    """Logs a warning message when datafeed v1 is used in the bot configuration
    """
    if version is not None and version.lower() == DF_V1:
        logging.warning(
            "The datafeed 1 service will be fully replaced by the datafeed 2 service in the future. "
            "Please consider migrating over to datafeed 2. For more information on the timeline as well as on "
            "the benefits of datafeed 2, please reach out to your Technical Account Manager or to our developer "
            "documentation https://docs.developers.symphony.com/building-bots-on-symphony/datafeed)")


class BdkDatafeedConfig:
    """Class holding datafeed specific configuration.
    """

    def __init__(self, config):
        """

        :param config: the dict containing the datafeed specific configuration.
        """
        self.version = DF_V2
        self.id_file_path = ""
        self.retry = BdkRetryConfig(dict(maxAttempts=BdkRetryConfig.INFINITE_MAX_ATTEMPTS))
        if config is not None:
            self.id_file_path = Path(config.get(DF_ID_FILE_PATH)) if DF_ID_FILE_PATH in config else ""
            log_dfv1_deprecation(config.get(VERSION))
            self.version = config.get(VERSION)
            if "retry" in config:
                self.retry = BdkRetryConfig(config.get("retry"))

    def get_id_file_path(self) -> Path:
        """

        :return: a Path instance of the datafeed.id file where to persist the datafeed.id (applicable for DFv1 only)
        :rtype: Path
        """
        return self.id_file_path if self.id_file_path else Path(".")
