from symphony.bdk.core.config.exception.bdk_config_exception import BdkConfigException
from symphony.bdk.core.config.bdk_config_parser import BdkConfigParser

from tests.utils.resource_utils import get_config_resource_filepath
import pytest


@pytest.fixture(params=["invalid_config.yaml"])
def invalid_config_path(request):
    return get_config_resource_filepath(request.param, as_text=False)


def test_parse_config_json():
    config_path = get_config_resource_filepath("config.json")
    with open(config_path) as json_file:
        config_data = BdkConfigParser.parse(json_file.read())
    assert config_data["bot"]["username"] == "youbot"


def test_parse_config_yaml():
    config_path = get_config_resource_filepath("config.yaml")
    with open(config_path) as yaml_file:
        config_data = BdkConfigParser.parse(yaml_file.read())
    assert config_data["bot"]["username"] == "youbot"


def test_parse_config_wrong_format(invalid_config_path):
    fail_error_message = "Config file is neither in JSON nor in YAML format."
    with pytest.raises(BdkConfigException, match=fail_error_message):
        with open(invalid_config_path) as invalid_config_file:
            BdkConfigParser.parse(invalid_config_file.read())

