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
            raise BdkConfigException(f"Config file has not been found at: {config_path.absolute()}")

    @classmethod
    def load_from_content(cls, content: str) -> BdkConfig:
        return cls.load_config(BdkConfigParser.parse(content))

    @staticmethod
    def load_config(data_dict: dict):
        return BdkConfig(**data_dict)

    @classmethod
    def load_from_symphony_dir(cls, relative_path: str):
        """Load BdkConfig from a relative path located in the .symphony directory.

        Note: The .symphony directory is located under your home directory.
        It's a convention adopted in order to avoid storing sensitive information (such as usernames, private keys...)
        within the code base.

        :param relative_path: configuration's relative path from the ``USER_HOME_PATH/.symphony`` directory
        :return: Symphony bot configuration object
        """
        config_path = (Path.home() / ".symphony" / relative_path).resolve()
        return cls.load_from_file(str(config_path))
