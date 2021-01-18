import yaml
import json
from symphony.bdk.core.config.exception.bdk_config_exception import BdkConfigException


class BdkConfigParser:
    """ Config Parser class

    Provide methods to Deserialize a configuration_content ``str``
    in a JSON or YAML format to a Python object.
    """

    @classmethod
    def parse(cls, config_content: str):
        config_data = cls.parse_input(config_content)
        if config_data is not None:
            return config_data
        raise BdkConfigException("Config file exists but is empty.")


    @staticmethod
    def parse_input(config_content: str):
        try:
            return json.loads(config_content)
        except json.JSONDecodeError:
            pass

        try:
            return yaml.safe_load(config_content)
        except yaml.YAMLError as e:
            pass

        raise BdkConfigException("Config file has a wrong format.")
