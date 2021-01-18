import json
from pathlib import Path

from symphony.bdk.core.config.bdk_config_parser import BdkConfigParser
from symphony.bdk.core.config.exception.bdk_config_exception import BdkConfigException
from symphony.bdk.core.config.model.bdk_config import BdkConfig


class BdkConfigLoader:

    @classmethod
    def load_from_file(cls, config_path: str):
        config_path = Path(config_path)
        if config_path.exists():
            config_content = config_path.read_text()
            return cls.load_from_content(config_content)
        else:
            raise BdkConfigException("Config file has not been found at: %s" % config_path.absolute())

    @classmethod
    def load_from_content(cls, content: str) -> BdkConfig:
        return cls.parse_config(BdkConfigParser.parse(content))

    @staticmethod
    def parse_config(json_tree):
        if json_tree is not None:
            return BdkConfig(**json_tree)
        else:
            raise BdkConfigException("Config file exists but is empty")

    @classmethod
    def load_from_symphony_dir(cls, relative_path: str):
        """Load BdkConfig from a relative path located in the .symphony directory.

        Note: The .symphony directory is located under your home directory (``System.getProperty("user.home")``).
        It's a convention adopted in order to avoid storing sensitive information (such as usernames, private keys...)
        within the code base.

        :param relative_path: configuration's relative path from the ``${user.home}/.symphony`` directory
        :return: Symphony bot configuration object
        """
        home_path = Path.home()
        symphony_dir_path = home_path / ".symphony"
        config_path = (symphony_dir_path / relative_path).resolve()

        if config_path.exists():
            return cls.load_from_content(config_path.read_text())
        else:
            raise BdkConfigException("Unable to load the configuration file from .symphony directory.")
