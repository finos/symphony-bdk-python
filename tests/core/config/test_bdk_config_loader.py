from tests.utils.resource_utils import get_config_resource_filepath
from symphony.bdk.core.config.bdk_config_loader import BdkConfigLoader
from symphony.bdk.core.config.exception.bdk_config_exception import BdkConfigException

import os
import pytest
from pathlib import Path
import uuid


@pytest.fixture(params=["config.json", "config.yaml"])
def simple_config_path(request):
    return get_config_resource_filepath(request.param)


@pytest.fixture(params=["config_global.json", "config_global.yaml"])
def global_config_path(request):
    return get_config_resource_filepath(request.param)


@pytest.fixture(params=["/wrong_path/config.json", "/wrong_path/wrong_extension.something"])
def wrong_path(request):
    return request.param


def test_load_from_file(simple_config_path):
    config = BdkConfigLoader.load_from_file(simple_config_path)
    assert config.bot.username == "youbot"


def test_load_from_content(simple_config_path):
    config_path = Path(simple_config_path)
    content = config_path.read_text()
    config = BdkConfigLoader.load_from_content(content)
    assert config.bot.username == "youbot"


def test_load_from_file_not_found(wrong_path):
    fail_error_message = "Config file has not been found at: %s" % Path(wrong_path).absolute()
    with pytest.raises(BdkConfigException, match=fail_error_message):
        config = BdkConfigLoader.load_from_file(wrong_path)


def test_main_test():
    print("CIRCLECI" in os.environ)


# TODO make sure that creating a file in home directory is an issue in circle ci
@pytest.mark.skipif(os.environ.get("CIRCLECI") == "true",
                    reason="CircleCI does not allow to create file in the home directory")
def test_load_from_symphony_directory(simple_config_path):
    tmp_config_filename = str(uuid.uuid4()) + "-config.yaml"
    tmp_config_path = Path.home() / ".symphony" / tmp_config_filename
    tmp_config_path.touch(exist_ok=True)
    resource_config_content = Path(simple_config_path).read_text()
    tmp_config_path.write_text(resource_config_content)
    config = BdkConfigLoader.load_from_symphony_dir(tmp_config_filename)
    assert config.bot.username == "youbot"


def test_load_client_global_config(global_config_path):
    config = BdkConfigLoader.load_from_file(global_config_path)
    assert config.pod.scheme == "https"
    assert config.pod.host == "diff-pod.symphony.com"
    assert config.pod.port == 8443
    assert config.pod.context == "context"

    assert config.scheme == "https"

    assert config.agent.scheme == "https"
    assert config.agent.host == "devx1.symphony.com"
    assert config.agent.port == 443
    assert config.agent.get_formated_context() == "/context"

    assert config.key_manager.scheme == "https"
    assert config.key_manager.host == "devx1.symphony.com"
    assert config.key_manager.port == 8443
    assert config.key_manager.get_formated_context() == "/diff-context"

    assert config.session_auth.scheme == "http"
    assert config.session_auth.host == "devx1.symphony.com"
    assert config.session_auth.port == 8443
    assert config.session_auth.context == "context"
