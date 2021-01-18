import yaml
import json
from symphony.bdk.core.config.exception.bdk_config_exception import BdkConfigException


class BdkConfigParser:

    @classmethod
    def parse(cls, config_content: str):
        config_data = cls.parse_input(config_content)
        return config_data

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

        raise BdkConfigException("Config file is not the right file type")
