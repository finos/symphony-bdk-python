import json

import yaml

from symphony.bdk.core.config.exception import BdkConfigException


class BdkConfigParser:
    """ Config Parser class

    Provide methods to Deserialize a configuration content
    as a ``str`` in a JSON or YAML format to a BdkConfig object.
    """

    @classmethod
    def parse(cls, config_content: str):
        """

        :param config_content:
        :return:
        """
        try:
            return json.loads(config_content)
        except json.JSONDecodeError:
            pass

        try:
            return yaml.safe_load(config_content)
        except yaml.YAMLError:
            pass

        raise BdkConfigException("Config file is neither in JSON nor in YAML format.")
