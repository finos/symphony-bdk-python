from pathlib import Path

from symphony.bdk.core.config.bdk_config_parser import BdkConfigParser
from symphony.bdk.core.config.exception import BdkConfigException
from symphony.bdk.core.config.model.bdk_config import BdkConfig


class BdkConfigLoader:
    """ Config loader class

    Provide methods to load a JSON or YAML configuration
    from an absolute path or `$HOME/.symphony``
    directory or string object to a BdkConfig object.
    """

    @classmethod
    def load_from_file(cls, config_path: str) -> BdkConfig:
        """Load config from an absolute filepath

        :param config_path: Configuration file absolute path
        :return Symphony bot configuration object
        """
        config_path = Path(config_path)
        if config_path.exists():
            config_content = config_path.read_text()
            return cls.load_from_content(config_content)
        raise BdkConfigException(f"Config file has not been found at: {config_path.absolute()}")

    @classmethod
    def load_from_content(cls, content: str) -> BdkConfig:
        """Load config from a string containing all config

        :param content: Content of the config file as one string.
        :return Symphony bot configuration object
        """
        data_dict = BdkConfigParser.parse(content)
        return BdkConfig(**data_dict)

    @classmethod
    def load_from_symphony_dir(cls, relative_path: str) -> BdkConfig:
        """Load BdkConfig from a relative path located in the .symphony directory.

        Note: The .symphony directory is located under your home directory.
        It's a convention adopted in order to avoid storing sensitive information (such as usernames, private keys...)
        within the code base.

        :param relative_path: configuration's relative path from the ``$HOME/.symphony`` directory
        :return: Symphony bot configuration object
        """
        config_path = (Path.home() / ".symphony" / relative_path).resolve()
        return cls.load_from_file(str(config_path))
